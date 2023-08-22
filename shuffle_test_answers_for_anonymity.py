import re
from random import shuffle

import pandas as pd

test_files = ["output_test_gpt-3.5-turbo.csv",
              "output_test_gpt-4.csv",
              "output_test_insolvency_bot_with_gpt-3.5-turbo.csv",
              "output_test_insolvency_bot_with_gpt-4.csv"]

df_all = []
for test_file in test_files:
    df = pd.read_csv(test_file, encoding="utf-8", sep="\t")
    df_all.append(df)

df = pd.concat(df_all)

question_to_responses = {}

for (q, qt), r in df.groupby(["question_no", "question_text"])["bot_response"]:
    four_responses = list(r)
    shuffle(four_responses)

    question_to_responses[int(re.sub(r'Q', '', q))] = (q, qt, four_responses)

with open("shuffled_questions_and_answers_for_eugenio.md", "w", encoding="utf-8") as f:
    for k in sorted(question_to_responses):
        q, qt, four_responses = question_to_responses[k]

        f.write(f"# {q}\n\n")
        f.write(f"> {qt}\n\n")
        for idx, r in enumerate(four_responses):
            f.write(f"Response {idx + 1}: {r}\n\n")
