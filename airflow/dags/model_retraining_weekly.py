from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from app.services.retraining_service import RetrainingService


def retrain_funds():
    return RetrainingService().retrain_fund()


with DAG(
    dag_id="fund_retraining_weekly",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * 0",
    catchup=False,
) as dag:
    PythonOperator(task_id="retrain_fund_model", python_callable=retrain_funds)
