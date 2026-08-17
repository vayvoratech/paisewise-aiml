# Mutual Fund Data Structure

The Week 7 recommendation service reads active schemes from `mf_schemes`.

Important fields used by the recommendation task:

- `scheme_name`
- `category`
- `risk_level`
- `returns_1y`
- `returns_3y`
- `returns_5y`
- `expense_ratio`
- `min_sip_amount`
- `amc_name`
- `fund_size_cr`

The raw NAV source is `data/NAVAll.txt`. It is kept as the real input file supplied for mutual fund scheme ingestion. No fake fund rows are inserted by the application.
