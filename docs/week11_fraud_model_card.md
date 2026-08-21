# Week 11 - Fraud Detection Model Card
## What the model does
Flags a transaction/login event as a fraud anomaly based on 7 features: device_changed, location_changed, time_since_registration, order_value, orders_last_30min, failed_mpin_count_24hr, login_count_today. It does not identify which of the 5 fraud categories applies - that's handled separately by the rule-based checks in `app/services/fraud_detection.py` (Week 10). This model is an additional, learned layer on top of those rules.
## Training data
`data/fraud_synthetic_data.csv` - 10,000 synthetic normal transactions and 500 synthetic anomaly transactions generated in Week 10, split 80/20 into train/test sets (stratified).
## Baseline performance (Isolation Forest, contamination=0.05)
- Precision: 0.680
- Recall: 0.700
- F1: 0.690
## Contamination tuning results
| Contamination | Precision | Recall | F1 |
|---|---|---|---|
| 0.01 | 1.000 | 0.160 | 0.276 |
| 0.02 | 0.972 | 0.350 | 0.515 |
| 0.05 | 0.680 | 0.700 | 0.690 |
| 0.1 | 0.441 | 0.830 | 0.576 |

## Local Outlier Factor comparison
- Precision: 0.104
- Recall: 0.140
- F1: 0.120

## Decision
Chosen model: **IsolationForest** with contamination=0.05, based on the highest F1 score (0.690) on the held-out test set.

## Known limitations
- Trained on synthetic data only, not real user transactions - real-world performance may differ once deployed against actual traffic patterns.
- The 5 anomaly categories were generated with fairly distinct, separable feature ranges (see Week 10 data generator), so this model has not been tested against subtler, more realistic fraud patterns.
- Category 2 (unusual trading velocity) is approximated using a 30-minute order count instead of the 2-minute window described in the original task, as noted in Week 10's documentation.
- Should be retrained periodically once real transaction data is available, rather than relying on synthetic data long-term.
