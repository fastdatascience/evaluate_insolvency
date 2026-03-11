'''
Run all train or test questions through GPT-3-5 Turbo or GPT-4

Usage: python generate_responses_gpt.py gpt-3.5-turbo|gpt-4 train|test

You need to set environment variable OPENAI_API_KEY first.
'''

import os
import re
import sys
import time
import traceback
import json
import pandas as pd
import requests

# imports for Gemini

from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel, ChatModel, InputOutputTextPair
from google.oauth2.service_account import Credentials
from vertexai.generative_models import GenerativeModel, ChatSession
import json, os, re
import vertexai

# end imports for Gemini

SUPPORTED_MODELS = {'gemini-2.0-pro-exp-02-05', 'gemini-2.5-pro'}
SUPPORTED_MODELS_CONCAT = '|'.join(SUPPORTED_MODELS)
COMMAND_LINE_PARAM = f"Usage: python generate_responses_gemini.py {SUPPORTED_MODELS_CONCAT} train|test"

if len(sys.argv) != 3:
    print(COMMAND_LINE_PARAM)
    exit()

    
MODEL = sys.argv[1]
if MODEL not in SUPPORTED_MODELS:
    print(COMMAND_LINE_PARAM)
    print("Please set model to one of ", " or ".join(SUPPORTED_MODELS))
    exit()
TRAIN_TEST = sys.argv[2]

print(f"Dataset: {TRAIN_TEST}")

# Begin get Gemini credentials
with open("/home/thomas/projects_internal/fds-social-media-manager/fds-social-media-automation-a88caa6fd5f2.json", "r", encoding="utf-8") as f:
  GOOGLE_APPLICATION_CREDENTIALS_ENV_VAR = f.read()

GOOGLE_APPLICATION_CREDENTIALS_JSON = re.sub("'.*?", '',
                                         re.sub(r'.+=\'', '', GOOGLE_APPLICATION_CREDENTIALS_ENV_VAR),
                                         re.MULTILINE)
GOOGLE_APPLICATION_CREDENTIALS_DICT = json.loads(GOOGLE_APPLICATION_CREDENTIALS_JSON)

credentials = Credentials.from_service_account_info(
GOOGLE_APPLICATION_CREDENTIALS_DICT,
scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
vertexai.init(
project=GOOGLE_APPLICATION_CREDENTIALS_DICT["project_id"],
credentials=credentials,
)
model = GenerativeModel(MODEL)
chat_session = model.start_chat()

def get_chat_response(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)
# End get Gemini credentials

df = pd.read_csv(f"{TRAIN_TEST}_questions.csv", encoding="utf-8", sep="\t")

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + os.environ["OPENAI_API_KEY"],
}

bot_responses = [""] * len(df)
bot_times = [0] * len(df)
bot_attempts = [0] * len(df)
for idx in range(len(df)):
    q = df.question_text.iloc[idx]
    q_no = df.question_no.iloc[idx]
    print(f"Asking question: {q_no}: {q}")

    starttime = time.time()

    json_data = {
        'model': MODEL,
        'messages': [
            {"role": "user", "content": q},
        ],
    }
    for attempt in range(3):
        print("attempt calling Gemini API:", attempt)
        try:
            prompt = q
            r = get_chat_response(chat_session, prompt)
            
            #response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=json_data)
            #r = response.json()["choices"][0]["message"]["content"]
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
