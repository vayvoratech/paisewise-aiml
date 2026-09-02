# Contribution Summary

## Navya Sree — Phase 1 AI Service

The supplied project contains `Investment Platform Phase 1 Tasks Documentation.docx`,
which documents Navya Sree's AI Service work:

- AI service foundation and modular FastAPI setup
- Prompt management
- Redis cache utility
- LLM wrapper
- Authentication middleware
- Sentry/error tracking configuration
- Financial jargon API
- AI safety guardrails
- Content filtering
- Redis rate limiting
- Logging and cost tracking
- Portfolio insight foundation
- Testing and integration readiness

## My Phase  implementation

The supplied repository's authoritative task map is
`docs/week1_to_week9_task_mapping.md`.

It covers:

- feature store and user extraction
- Airflow and MLflow
- financial-jargon data/evaluation
- financial AI safety
- portfolio insight data and pipelines
- behaviour features and incremental updates
- mutual-fund recommendation
- Week 8 recommendation validation and feedback tooling
- Week 9 paper-trade coaching

## Integration note

The original archive contained both an older AI-service route layer and a newer
`app/` implementation. The cleaned project keeps both codebases where they
provide distinct functionality, while `main.py` exposes a single consolidated
FastAPI application and avoids duplicate registrations of overlapping endpoints.

Actual human review/feedback is not fabricated. Evaluation fixtures are clearly
kept under `evaluation/`.
