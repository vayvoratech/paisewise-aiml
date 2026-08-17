# LLM Prompt Testing

Week 2 requires testing 50 financial-jargon terms with different prompt styles.

The project provides `scripts/run_jargon_prompt_tests.py`.

It reads the first 50 terms from `data/financial_terms.csv` and tests these prompt styles:

1. simple explanation
2. explanation with analogy
3. bullet-point explanation
4. explanation with a practical example
5. simple Hindi explanation

The script writes the actual model responses to `data/jargon_prompt_results.csv` when it is run with a valid Gemini configuration.

No model responses are hardcoded into the application.

## Recording the best prompt

After the 50-term run, compare the output for clarity, accuracy, beginner friendliness and usefulness. Record the selected prompt in the task report rather than committing fabricated test results.
