# Week 3 - Prompt Revision Workflow

The 100-response evaluator produces six quality scores.

`review_jargon_quality.py` groups the real evaluation results by term,
calculates the average score and identifies the worst-performing terms.

For each low-scoring term the recommended revision areas are:

- clarity
- beginner friendliness
- analogy relevance
- accuracy

The workflow is:

1. Run the 100-response evaluator on real LLM responses.
2. Run `review_jargon_quality.py`.
3. Review the lowest-scoring terms.
4. Update the relevant prompt style.
5. Re-run the evaluation.
6. Keep the revised prompt only when the quality improves.

This avoids claiming that an LLM prompt was improved without actually
comparing the before/after evaluation results.
