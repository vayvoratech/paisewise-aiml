# Week 1-7 final preflight

Use this sequence after extracting the project. It checks the real application
database before running the Week 6/7 Airflow workflows.

## 1. Environment

```bash
cd /mnt/c/Projects/financial-ai-platform
source .venv/bin/activate
export AIRFLOW__CORE__DAGS_FOLDER=/mnt/c/Projects/financial-ai-platform/airflow/dags
```

## 2. Sync the application-owned Week 6 schema

```bash
python -m scripts.sync_user_features_schema
```

## 3. Run the behaviour feature pipeline

```bash
python -m app.pipelines.feature_pipeline
```

## 4. Validate Airflow DAG discovery

```bash
airflow dags list --local | grep -E "financial_ai_test_dag|feature_store_pipeline|portfolio_insight_daily"
```

## 5. Test the feature-store DAG

```bash
airflow dags test feature_store_pipeline 2026-08-14
```

## 6. Test the basic Airflow DAG

```bash
airflow dags test financial_ai_test_dag 2026-08-14
```

## 7. Run the automated tests

```bash
pytest -q
```

A successful unit-test run does not replace testing against the real
PostgreSQL schema. The schema-sync and DAG tests above are intentionally kept
separate for that reason.
