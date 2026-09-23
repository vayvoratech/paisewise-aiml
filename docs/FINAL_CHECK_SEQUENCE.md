# Final W1-W15 check sequence

From the project root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/WSL: source .venv/bin/activate
pip install -r requirements.txt
```

Then:

```bash
python -m compileall -q .
python scripts/create_phase2_tables.py
python scripts/evaluate_phase2.py
pytest -q
python scripts/integration_smoke_test.py
uvicorn main:app --reload
```

After startup open Swagger at `/docs` and verify:

- `/ai/jargon`
- `/ai/portfolio-insight`
- `/features/{userId}`
- `/ai/features/refresh/{userId}`
- `/ai/fund-recommend`
- `/ai/recommendation-click`
- `/ai/paper-trade-coach`
- `/ai/fraud-check`
- `/ai/fraud-alerts`
- `/ai/next-lessons`
- `/ai/lesson-difficulty/{lessonId}/{userId}`
- `/ai/sip-coach`
- `/ai/sip-scenario`
- `/ai/stock-discovery/{userId}`

Environment-dependent checks must be run with PostgreSQL, Redis, Kafka and MLflow available. Airflow should load both `feature_store_pipeline`, `portfolio_insight_daily`, and `sip_coach_monthly`.
