# Final Week 1-7 Verification

Checks performed before packaging the final Week 7 project:

- Python syntax check: `python -m compileall -q app airflow scripts tests`
- Automated tests: 13 tests passed
- Financial terms file: 200 terms present in `data/financial_terms.csv`
- Excel terms database: `data/financial_terms.xlsx` generated from the 200-term CSV
- No `.env` file is included
- No Python cache folders are included
- No random/demo user behaviour loader is included
- No hardcoded sample market movement is included
- Week 7 API and scoring files compile successfully

External services such as PostgreSQL, Gemini, Alpha Vantage, NewsAPI, Slack and Airflow still require the user's local environment variables/services when the project is run.
