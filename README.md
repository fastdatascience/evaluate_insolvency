# evaluate_insolvency

The training questions are in `train_questions.csv`.

## Running all the training questions through GPT

```
python generate_responses_gpt.py gpt-3.5-turbo train
python generate_responses_gpt.py gpt-4 train
```

## Running all the test questions through GPT

```
python generate_responses_gpt.py gpt-3.5-turbo test
python generate_responses_gpt.py gpt-4 test
```