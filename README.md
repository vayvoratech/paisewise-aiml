# Financial AI Platform - Weeks 1 to 9

This repository contains the implementation for the Week 1-9 task set.

The code is intentionally simple and easy to explain in a review.

## Main flows

### Portfolio insight

```text
User with real holdings
        ↓
PostgreSQL
        ↓
Airflow daily DAG
        ↓
Market + sector + top 3 news
        ↓
AI service
        ↓
MLflow tracking
        ↓
portfolio_insights
        ↓
Slack alert on batch errors
```

### Mutual-fund recommendation

```text
User goal + risk + horizon + amount
        ↓
Active mf_schemes
        ↓
Risk eligibility
        ↓
Week 8 exclusions
        ↓
40/30/20/10 scoring
        ↓
Goal + horizon suitability
        ↓
Category/AMC diversity
        ↓
Top 3 funds
        ↓
One-sentence LLM reason
```

Week 8 rules include:

- beginner + expense ratio above 1.5% → exclude
- horizon below 3 years + ELSS → exclude
- prefer three different categories and AMCs

### Paper-trade coach

```text
Paper-trade order
        ↓
Trade context extractor
        ↓
Price / 52-week range / volume / sector / learning history
        ↓
Week 9 rubric
        ↓
Educational coach feedback
```

The coach does not guarantee returns or issue real-money buy/sell instructions.

## Indian language support

The service supports all **22 languages listed in the Eighth Schedule**:

Assamese, Bengali, Bodo, Dogri, Gujarati, Hindi, Kannada, Kashmiri,
Konkani, Malayalam, Manipuri, Marathi, Maithili, Nepali, Odia, Punjabi,
Sanskrit, Santali, Sindhi, Tamil, Telugu and Urdu.

The catalogue is in `data/indian_languages.csv`.

Use:

```text
GET /ai/languages
```

Portfolio insight and fund explanations can use a supported language code or
language name.

English is retained only as an internal fallback; it is not counted among the
22 scheduled Indian languages.

## Week 8 evaluation

The 20 profiles in `evaluation/week8_user_profiles.json` are synthetic
evaluation fixtures required by the task. They are **not application seed
data** and are never inserted into PostgreSQL.

The Week 9 30 scenarios are also training/evaluation fixtures and are not
inserted into application tables.

## No application sample data

The application does not seed fake users, holdings, behaviour or market
movements.

## Week 8 human feedback

The repository includes a five-reviewer feedback template and code that
normalizes reviewer ratings into revised recommendation weights.

Actual internal feedback must come from the five real reviewers. It is not
fabricated.

## Environment

Create a local `.env` file and keep it out of Git:

```text
DATABASE_URL=postgresql+psycopg2://...
GEMINI_API_KEY=...
GEMINI_MODEL=...
ALPHA_VANTAGE_API_KEY=...
NEWS_API_KEY=...
AI_SERVICE_URL=http://127.0.0.1:8000/ai/portfolio-insight
SLACK_WEBHOOK=...
MARKET_SYMBOLS=...
```

## Run API

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

## Tests

```bash
pytest -q
```

## Important

The repository expects the real company PostgreSQL schema/data to exist.
Production credentials and production data are not included.
