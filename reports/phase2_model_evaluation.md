# Phase 2 Week 15 Model Evaluation

| Component | Required cases | Result |
|---|---:|---|
| Fund recommender | 30 profiles | avg 0.2 ms, max 2.17 ms |
| Fraud detector | 50 scenarios | 23 flagged |
| Lesson personalizer | 10 profiles | 10 paths generated |
| SIP coach | 20 scenarios | statuses: underfunded, way_behind |
| Stock discovery | 15 profiles | 5-5 stocks returned |

## Notes
- Evaluation uses deterministic synthetic profiles/scenarios.
- It checks implementation behavior and latency locally; external Spring Boot, Kafka, Redis, PostgreSQL and deployment verification still require the environment to be running.