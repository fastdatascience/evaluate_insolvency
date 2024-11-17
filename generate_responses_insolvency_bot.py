'''
Run all train or test questions through Insolvency Bot

Usage: python generate_responses_insolvency_bot.py gpt-3.5-turbo|gpt-4 train|test

You need to set environment variable OPENAI_API_KEY first.
'''

import os
import re
import sys
import time
import traceback
import pandas as pd
import requests
sys.path.append("../insolvency/")
from insolvency_bot import answer_question

SUPPORTED_MODELS = {'gpt-3.5-turbo', 'gpt-4', 'gpt-4o'}
SUPPORTED_MODELS_CONCAT = '|'.join(SUPPORTED_MODELS)
COMMAND_LINE_PARAM = f"Usage: python generate_responses_insolvency_bot.py {SUPPORTED_MODELS_CONCAT} train|test"

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

df = pd.read_csv(f"{TRAIN_TEST}_questions.csv", encoding="utf-8", sep="\t")

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + os.environ["OPENAI_API_KEY"],
}

bot_responses = [""] * len(df)
bot_times = [0] * len(df)
bot_attempts = [0] * len(df)
bot_statutes = [""] * len(df)
bot_cases = [""] * len(df)
bot_forms = [""] * len(df)
for idx in range(len(df)):
    q = df.question_text.iloc[idx]
    q_no = df.question_no.iloc[idx]
    print(f"Asking question: {q_no}: {q}")

    starttime = time.time()

    for attempt in range(3):
        print("attempt calling GPT API:", attempt)
        try:
            insolvency_bot_response_json = answer_question(q, False, MODEL)
            r = insolvency_bot_response_json["_response"]
            statutes = "|".join(insolvency_bot_response_json["legislation"])
            cases = "|".join(insolvency_bot_response_json["cases"])
            forms = "|".join(insolvency_bot_response_json["forms"])
            break
        except:
            print("Try again")
            traceback.print_exc()
            time.sleep(10)

    bot_responses[idx] = re.sub(r'\s+', ' ', r)

    endtime = time.time()
    bot_times[idx] = endtime - starttime
    bot_attempts[idx] = attempt + 1
    bot_statutes[idx] = statutes
    bot_cases[idx] = cases
    bot_forms[idx] = forms

    print("\tReceived response: ", r)

df["bot_response"] = bot_responses
df["bot_response_time"] = bot_times
df["bot_response_attempts"] = bot_attempts
df["bot_statutes"] = bot_statutes
df["bot_cases"] = bot_cases
df["bot_forms"] = bot_forms

df.to_csv(f"output_{TRAIN_TEST}_insolvency_bot_with_{MODEL}.csv", sep="\t", encoding="utf-8", index=False)
