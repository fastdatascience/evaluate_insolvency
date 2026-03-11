'''
Run all train or test questions through GPT-3-5 Turbo or GPT-4

Usage: python generate_responses_gpt.py gpt-3.5-turbo|gpt-4 train|test

You need to set environment variable CLAUDE_API_KEY first.
'''

import os
import re
import sys
import time
import traceback

import pandas as pd
import requests

# begin Claude imports
from anthropic import Anthropic
# end Claude imports

SUPPORTED_MODELS = {'claude-3-5-sonnet-20241022', 'claude-opus-4-6'}
SUPPORTED_MODELS_CONCAT = '|'.join(SUPPORTED_MODELS)
COMMAND_LINE_PARAM = f"Usage: python generate_responses_gpt.py {SUPPORTED_MODELS_CONCAT} train|test"

if len(sys.argv) != 3:
    print(COMMAND_LINE_PARAM)
    exit()

if os.environ.get("CLAUDE_API_KEY") == "" or os.environ.get("CLAUDE_API_KEY") is None:
    print("Please set environment variable CLAUDE_API_KEY first.")
    exit()

MODEL = sys.argv[1]
if MODEL not in SUPPORTED_MODELS:
    print(COMMAND_LINE_PARAM)
    print("Please set model to one of ", " or ".join(SUPPORTED_MODELS))
    exit()
TRAIN_TEST = sys.argv[2]

print(f"Dataset: {TRAIN_TEST}")

df = pd.read_csv(f"{TRAIN_TEST}_questions.csv", encoding="utf-8", sep="\t")

## begin Claude logic

def ask_claude(question, model):
    # Initialize the client with your API key
    client = Anthropic(api_key=os.environ["CLAUDE_API_KEY"])  # Replace with your actual API key
    
    # Create a message
    message = client.messages.create(
        model=model,
        max_tokens=2000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )
    
    # Return the response
    return message.content[0].text

## end Claude logic

bot_responses = [""] * len(df)
bot_times = [0] * len(df)
bot_attempts = [0] * len(df)
for idx in range(len(df)):
    q = df.question_text.iloc[idx]
    q_no = df.question_no.iloc[idx]
    print(f"Asking question: {q_no}: {q}")

    starttime = time.time()

    for attempt in range(3):
        print("attempt calling Claude API:", attempt)
        try:
            r = ask_claude(q, MODEL)
            break
        except:
            print("Try again")
            traceback.print_exc()
            time.sleep(10)
    bot_responses[idx] = re.sub(r'\s+', ' ', r)

    endtime = time.time()
    bot_times[idx] = endtime - starttime
    bot_attempts[idx] = attempt + 1

    print("\tReceived response: ", r)

df["bot_response"] = bot_responses
df["bot_response_time"] = bot_times
df["bot_response_attempts"] = bot_attempts

df.to_csv(f"output_{TRAIN_TEST}_{MODEL}.csv", sep="\t", encoding="utf-8", index=False)
