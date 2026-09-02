# Implementation handoff

## Current delivery boundary

This delivery hardens the functionality already present in the supplied project and
stops at the project's current fraud/model stage. The later roadmap items that are not
represented by the supplied implementation are intentionally not fabricated.

## Included hardening

- Canonical `main.py` ASGI entrypoint and `app.main:app` compatibility.
- Internal `X-API-KEY` authentication middleware with explicit local-development bypass.
- Central prompt constants and financial guardrails.
- English/Hindi jargon prompt variants.
- Redis JSON cache with graceful cache failure handling.
- Top-100 jargon cache warming from `data/financial_terms.csv`.
- Gemini wrapper with 3 attempts, exponential backoff and a 30-second call timeout.
- Sentry initialization and exception capture on handled LLM failures.
- Jargon DB fallback aligned to `learn.jargon_terms` from the supplied schema.
- Portfolio insight API uses backend-supplied context only; no application DB query.
- Daily portfolio cache key includes user/date/language and TTL ends at local midnight.
- Portfolio LLM response quality gate of 50-200 words and required fallback template.
- Request/token/cost logging and daily INR budget alert utility.
- Feature API aligned to canonical `user_features` columns.
- Fund catalogue aligned to canonical `mf_schemes` table.
- Paper-trade feature lookup aligned to canonical feature columns.
- Fraud inference endpoint with model score, 0-100 risk score, thresholds and five rule flags.
- Canonical portfolio batch pipeline queries `auth.users`, `profile.profiles`, and `portfolio.holdings`.
- Portfolio insight persistence aligned to the supplied `portfolio_insights` schema.
- Optional recommendation A/B support tables isolated in `database/ai_support_schema.sql`.
- Dockerfile, local Redis compose file, API contract and environment documentation.

## Database source of truth

The supplied `final_db_schema(1).docx` is treated as the authoritative application schema.
The AI service does not auto-create tables when opening a database connection.

The only additional SQL in `database/ai_support_schema.sql` is for recommendation experiment
tracking because those two support tables were already referenced by the supplied code but
were not present in the supplied schema document.
