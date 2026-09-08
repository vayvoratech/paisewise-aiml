# Airflow Local Setup

The project is intended to run Airflow inside WSL/Linux rather than directly on Windows.

## Start Airflow

```bash
source .venv/bin/activate
airflow standalone
```

Open:

`http://localhost:8080`

## DAGs in this project

- `financial_ai_test_dag` - Week 1 setup check. Runs manually.
- `feature_store_pipeline` - Week 1/6 feature-store pipeline.
- `portfolio_insight_daily` - Week 6 daily portfolio insight pipeline.

The portfolio DAG uses the Asia/Kolkata timezone and is scheduled for **16:10 IST Monday-Friday**.

## Important

The DAGs read real PostgreSQL data and external API data. No simulated users or random behaviour records are inserted by the project.
