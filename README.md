# evaluate_insolvency

The training questions are in `train_questions.csv`.

To run the models and evaluation, you need to run all these scripts in sequence:

## Running all the training questions through GPT

```
python generate_responses_gpt.py gpt-3.5-turbo train
python generate_responses_gpt.py gpt-4 train
```

## Running all the training questions through the insolvency bot with two underlying LLMs (GPT-3.5-Turbo and GPT-4)

```
python generate_responses_insolvency_bot.py gpt-3.5-turbo train
python generate_responses_insolvency_bot.py gpt-4 train
```

## Running all the test questions through GPT

```
python generate_responses_gpt.py gpt-3.5-turbo test
python generate_responses_gpt.py gpt-4 test
```

## Running all the test questions through the insolvency bot with two underlying LLMs (GPT-3.5-Turbo and GPT-4)

```
python generate_responses_insolvency_bot.py gpt-3.5-turbo test
python generate_responses_insolvency_bot.py gpt-4 test
```

## Evaluating the models

```
python evaluate_responses_with_mark_scheme.py gpt-3.5-turbo train
python evaluate_responses_with_mark_scheme.py gpt-4 train
python evaluate_responses_with_mark_scheme.py insolvency_bot_with_gpt-3.5-turbo train
python evaluate_responses_with_mark_scheme.py insolvency_bot_with_gpt-4 train
python evaluate_responses_with_mark_scheme.py gpt-3.5-turbo test
python evaluate_responses_with_mark_scheme.py gpt-4 test
python evaluate_responses_with_mark_scheme.py insolvency_bot_with_gpt-3.5-turbo test
python evaluate_responses_with_mark_scheme.py insolvency_bot_with_gpt-4 test
```