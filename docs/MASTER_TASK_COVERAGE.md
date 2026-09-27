# PaiseWise master implementation coverage

This is the final integration checklist. The final ZIP must contain an implementation and test/evaluation path for every item below.

## Phase 1 + Phase 2
- Core FastAPI AI service and authentication
- Feature store extraction, validation, incremental updates and refresh
- 200 financial terms, multilingual jargon, prompt evaluation and safety guardrails
- Portfolio insight, market data, top news, batching, persistence, fallback and Slack failure alerts
- Fund catalogue, recommendation scoring, exclusions, diversity, explanations, refresh, cache and A/B support
- Paper-trade coach and trading concepts
- Fraud event collection, features, model inference, thresholds and compliance alerts
- Lesson personalization, difficulty and learning profile
- SIP coach, scenarios, Monte Carlo and monthly Airflow reporting
- Stock discovery with learning-level, F&O and beginner safety rules
- Phase 2 evaluation, regression, fallback and security checks

## Akhil Phase 3
- RAG architecture and full knowledge base
- 30 lessons + financial jargon ingestion
- ChromaDB collection `paisewise_knowledge_base`
- 200-word chunking with overlap
- Sentence-transformer embeddings
- Top-10 retrieval followed by reranking and top-5 context
- Retrieval evaluation and refresh script
- 50 advice-deflection tests + 50 educational tests
- Guardrail precision/recall evaluation
- Hindi multilingual evaluation
- Red-team bypass tests
- Portfolio diversification, concentration, score, beta, drawdown and correlation
- Weekly portfolio health reporting
- Churn definition, training data, Day-7 feature engineering, XGBoost training and evaluation
- Daily churn scoring
- News ingestion, sector classification, sentiment, sector aggregation and market context
- Weekly fund retraining and >2% deployment gate
- Monthly churn retraining with MLflow metrics and deployment gate

## Srikanth Phase 3
- POST `/ai/chat`
- Last-10-message Redis context with 4-hour TTL
- User profile and portfolio summary injection
- Guardrail topic detection and SEBI-advisor deflection
- Streaming chat
- Chat feedback and weekly analytics
- 100-session performance test with <8 second target
- Portfolio analytics API and LLM health report
- Weekly portfolio analytics Airflow job for users with >2 holdings
- NIFTY 50 / sector comparison
- SIP ₹1,000 what-if analysis
- Portfolio analytics history
- Daily churn DAG at 9 AM
- `user_churn_scores` persistence
- Kafka `notifications.push` intervention path
- Churn-risk API and LLM re-engagement messages
- 50/50 AI vs template re-engagement experiment
- 7-day re-engagement tracking and weekly dashboard
- Market context API
- Stock news API with three relevant items and sentiment
- Sector news digest in Hindi/English path
- Two-hour news cache
- Model versioning, metrics and dataset versions
- MLflow registry support
- Shadow comparison
- >5% anomaly rollback support
- Slack retraining notification support
- Retraining schedule documentation

## Lead integration contract
`Backend -> JSON -> AI service -> validation/preprocessing -> model/LLM -> response validation/fallback -> JSON`

## Non-fabricated external work
Human domain review and actual five-person feedback must come from real reviewers. The repository contains the rubric, feedback template and evaluation tooling but does not invent human evidence.
