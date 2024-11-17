'''
Evaluate Insolvency Bot or GPT against mark scheme

Usage: python evaluate_bot_responses_with_mark_scheme.py gpt-3.5-turbo|gpt-4|insolvency_bot_with_gpt-3.5-turbo|insolvency_bot_with_gpt-4 train|test

You need to set environment variable OPENAI_API_KEY first.
'''

import json
import os
import sys
import time
import traceback
import re
import pandas as pd
import requests

SUPPORTED_MODELS = {'gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'insolvency_bot_with_gpt-3.5-turbo', 'insolvency_bot_with_gpt-4', 'insolvency_bot_with_gpt-4o'}
SUPPORTED_MODELS_CONCAT = '|'.join(SUPPORTED_MODELS)
COMMAND_LINE_PARAM = f"Usage: python evaluate_bot_responses_with_mark_scheme.py {SUPPORTED_MODELS_CONCAT} train|test"


if len(sys.argv) != 3:
    print(COMMAND_LINE_PARAM)
    exit()

if os.environ.get("OPENAI_API_KEY") == "" or os.environ.get("OPENAI_API_KEY") is None:
    print("Please set environment variable OPENAI_API_KEY first.")
    exit()

MODEL = sys.argv[1]
if MODEL not in SUPPORTED_MODELS:
    print(COMMAND_LINE_PARAM)
    print("Please set model to one of ", " or ".join(SUPPORTED_MODELS))
    exit()
TRAIN_TEST = sys.argv[2]

print(f"Dataset: {TRAIN_TEST}")

df_mark_scheme = pd.read_csv(f"{TRAIN_TEST}_mark_scheme.csv", encoding="utf-8", sep="\t")

df = pd.read_csv(f"output_{TRAIN_TEST}_{MODEL}.csv", encoding="utf-8", sep="\t")

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + os.environ["OPENAI_API_KEY"],
}

column_to_evaluate = 'bot_response'

re_yes = re.compile(r'(?i)\b(?:yes|definitely|certainly)\b')
re_maybe = re.compile(r'(?i)\b(?:maybe|however|but|correct)\b')
re_mention_insolvency_act = re.compile(r'(?i)\b(?:ia|insolvency act|1986)\b')
re_mention_companies_act = re.compile(r'(?i)\b(?:ca|companies act|2006)\b')

question_no_to_max_points_available = dict(df_mark_scheme.groupby("question_no").sum()["points"])

mark_scheme_col = [""] * len(df)
mark_scheme_assessments = [""] * len(df)
scores = [0] * len(df)
scores_broken_down = [""] * len(df)
max_points_available  = [0] * len(df)
for idx in range(len(df)):
    question_no = df.question_no.iloc[idx]
    answer = df[column_to_evaluate].iloc[idx]

    if question_no in set(df_mark_scheme.question_no):
        max_points_available[idx] = question_no_to_max_points_available[question_no]
        print("EVALUATING ANSWER: ", answer)
        print("MARK SCHEME QUESTION", question_no)
        rows = df_mark_scheme[df_mark_scheme.question_no == question_no]
        criteria = list(rows.criterion)
        points = list(rows.points)
        mark_scheme_col[idx] = json.dumps([criteria, points])
        score = 0
        scores_this_q = []
        for j in range(len(rows)):
            criterion = criteria[j]
            criterion = re.sub(r'\s+', ' ', criterion)
            print("\nCRITERION: ", criterion)

            if pd.isna(answer) or answer is None:
                continue

            json_data = {
                'model': 'gpt-4',  # We always use GPT-4 for evaluation, whether or not we used it inside the model.
                'messages': [
                    {"role": "user", "content": "The following is a lawyer's response to a question."},
                    {"role": "user", "content": answer},
                    {"role": "user", "content": criterion},
                    {"role": "user", "content": 'Answer with "yes", "no", or "maybe".'}
                ],
                "max_tokens":10
            }
            for attempt in range(3):
                print("attempt", attempt)
                try:
                    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers,
                                             json=json_data)
                    time.sleep(18)  # avoid rate limiting by OpenAI
                    if response.status_code != 200:
                        print ("\tResponse status code =", response.status_code)
                        if attempt < 2:
                            print("\tTry again")
                        time.sleep(10)
                        continue
                    r = response.json()["choices"][0]["message"]["content"]
                    r = re.sub(r'\s+', ' ', r)
                    break
                except:
                    print ("\tException encountered when calling OpenAI API.")
                    if attempt < 2:
                        print("\tTry again")
                    traceback.print_exc()
                    time.sleep(10)

            print(column_to_evaluate, idx, question_no, r)
            mark_scheme_assessments[idx] += r + "|"

            r = r.strip()

            s = 0
            if re_yes.findall(r):
                s = points[j]
            elif re_maybe.findall(r):
                s = points[j] / 2
            elif re_mention_insolvency_act.findall(criterion) and re_mention_insolvency_act.findall(answer):
                s = points[j] / 2
                print ("\tBoth bot answer and assessment criterion mention Insolvency Act, although not necessarily same section. Half points awarded.")
            elif re_mention_companies_act.findall(criterion) and re_mention_companies_act.findall(answer):
                s = points[j] / 2
                print(
                    "\tBoth bot answer and assessment criterion mention Companies Act, although not necessarily same section. Half points awarded.")

            print (f"\tScore for this criterion: {s}")
            score += s
            scores_this_q.append(s)

        scores[idx] = score
        scores_broken_down[idx] = json.dumps(scores_this_q)
df["mark_scheme"] = mark_scheme_col
df["bot_score"] = scores
df["bot_score_breakdown"] = scores_broken_down
df["max_points_available"] = max_points_available
df["bot_mark_scheme_assessments"] = mark_scheme_assessments

# Add an extra row for the totals
df_totals_row = pd.DataFrame()
for c in df.columns:
    df_totals_row[c] = [""]

df_totals_row["question_no"] = "TOTAL"
df_totals_row["max_points_available"] = df["max_points_available"].sum()
df_totals_row["bot_score"] = df["bot_score"].sum()
df = pd.concat([df, df_totals_row])

df.to_csv(f"scores_{TRAIN_TEST}_{MODEL}.csv", sep="\t", encoding="utf-8", index=False)
