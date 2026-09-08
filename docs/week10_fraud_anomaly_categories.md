# Week 10 - Fraud and Anomaly Categories (PaiseWise)

## Categories

**Category 1: Account takeover**
New device used to log in, followed by a large withdrawal on the same day.

**Category 2: Unusual trading velocity**
10+ orders placed in a very short window (2 minutes).
Note: our feature set only tracks `orders_last_30min` (not a 2-minute
count), so this category is approximated using a threshold on the
30-minute count instead of an exact 2-minute count. See
`app/services/fraud_detection.py` for the threshold used.

**Category 3: New account large order**
Account is less than 7 days old and places an order greater than
INR 50,000.

**Category 4: Impossible location change**
Login from one city, then a login from a different, far-away city a
short time later (e.g. Mumbai, then Delhi 30 minutes later). Our
feature set stores this as a precomputed boolean (`location_changed`)
rather than raw login timestamps/cities, so the "impossible" time
check itself is expected to happen upstream, before this feature is
set to `True`.

**Category 5: Multiple failed MPIN attempts + immediate large order**
Several failed MPIN attempts, followed by a successful login and an
immediate large order.

## Feature set for the fraud model

| Feature | Type | Meaning |
|---|---|---|
| device_changed | boolean | Login used a device not seen before for this user |
| location_changed | boolean | Login city differs from the user's usual/recent city in a way that looks impossible given the time gap |
| time_since_registration | number (days) | How old the account is |
| order_value | number (INR) | Value of the order being placed |
| orders_last_30min | number | Count of orders placed by this user in the last 30 minutes |
| failed_mpin_count_24hr | number | Failed MPIN attempts in the last 24 hours |
| login_count_today | number | Number of logins today |

## Synthetic training data

`scripts/generate_fraud_synthetic_data.py` generates 10,000 normal
transactions and 500 anomaly examples (roughly distributed across the
5 categories above) and saves them to
`data/fraud_synthetic_data.csv`.

`scripts/explore_fraud_synthetic_data.py` reads that CSV and saves
histogram comparisons (normal vs anomaly) for each feature to
`data/fraud_plots/`.
