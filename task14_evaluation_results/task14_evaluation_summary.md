# Task 14 - Evaluation Summary

## Task 7 AI Component Evaluation

**Result: 20/20 tests passed.**

## Fraud Model Benchmark

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.65 | 0.6364 | 0.7 | 0.6667 | 0.575 |
| Random Forest | 0.575 | 0.5652 | 0.65 | 0.6047 | 0.5625 |
| HistGradientBoosting | 0.575 | 0.56 | 0.7 | 0.6222 | 0.5938 |

> The fraud benchmark uses synthetic development data. These results are not production validation.

## Evidence

The complete pytest and benchmark output is preserved in `task14_evaluation_evidence.json`.