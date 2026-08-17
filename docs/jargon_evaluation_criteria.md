# Jargon Explanation Evaluation Criteria

Week 3 evaluates generated financial-jargon explanations for beginner investors.

Each response is scored from 1 to 5 on:

| Criterion | Meaning |
|---|---|
| Clarity | Is the explanation easy to understand? |
| Accuracy | Is the financial meaning correct? |
| Analogy relevance | Is the analogy relevant when one is used? |
| Beginner friendliness | Is difficult jargon avoided or explained? |
| Completeness | Are the important parts of the term covered? |
| Language quality | Is the wording natural and grammatically correct? |

Run the automated evaluator with:

```bash
python scripts/evaluate_jargon_responses.py data/jargon_prompt_results.csv --limit 100
```

The evaluator sends each response to the LLM for scoring and writes the real scores to a CSV report. It does not create fake evaluation results.
