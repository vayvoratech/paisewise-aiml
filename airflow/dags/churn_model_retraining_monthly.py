from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from app.services.retraining_service import RetrainingService


def retrain_churn():
    return RetrainingService().retrain_churn()


with DAG(
    dag_id="churn_model_retraining_monthly",
    start_date=datetime(2026, 1, 1),
    schedule="0 3 1 * *",
    catchup=False,
) as dag:
    PythonOperator(task_id="retrain_churn_model", python_callable=retrain_churn)
