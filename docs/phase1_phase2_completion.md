# PaiseWise Phase 1 + Phase 2 completion map

This document is the implementation checklist for the combined cumulative AI service.

## Navya W1-W5
- Base service structure, prompt constants, Redis cache, LLM wrapper, auth and Sentry
- Jargon endpoint, cache-first behavior, cache warming and DB fallback
- Guardrails/content filtering, rate limiting and cost utility
- Portfolio insight endpoint, context, cache and fallback
- Batch/DAG/timeout/quality checks and deployment documentation

## Phase 2 W6-W15
- W6 feature serving, refresh, monitoring, version field and daily quality report
- W7/W8 fund recommendation, diversity, exclusions, A/B tracking, refresh and cache
- W9 paper-trade coach
- W10/W11 fraud collector, features, model, scoring and thresholds
- W12 lesson personalization
- W13 SIP coach, Monte Carlo and monthly Airflow report
- W14 stock discovery with learning-level and F&O/penny-stock rules
- W15 five-component evaluation, 500-request local integration test and fallback/security checks

## Important runtime verification
Code coverage is included in the ZIP. After extraction, run the test suite and environment-dependent checks with PostgreSQL/Redis/Kafka/Airflow configured. AWS/Render deployment itself cannot be proven by a source ZIP alone.
