from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

def check_airflow_setup():

    print("Airflow test DAG is running successfully.")


with DAG(
    dag_id="financial_ai_test_dag",

    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["setup"],

) as dag:
    test_task = PythonOperator(


        
        task_id="check_airflow_setup",
        python_callable=check_airflow_setup,
    )
