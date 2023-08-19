# evaluate_insolvency

The training questions are in `train_questions.csv`.

To run the models and evaluation, you need to run all these scripts in sequence:

## Running all the development/training questions through GPT

These were questions that were used to develop the model and can't be used for validation. We run the questions through GPT to get a control for the baseline performance.

```
python generate_responses_gpt.py gpt-3.5-turbo train
python generate_responses_gpt.py gpt-4 train
```

## Running all the development/training questions through the insolvency bot with two underlying LLMs (GPT-3.5-Turbo and GPT-4)

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
