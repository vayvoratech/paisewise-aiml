import os
import sys
import pendulum
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from airflow import DAG

from airflow.providers.standard.operators.python import PythonOperator

from app.pipelines.feature_pipeline import run_behaviour_feature_pipeline


with DAG(

    dag_id="feature_store_pipeline",
    start_date=pendulum.datetime(2026, 1, 1, tz="Asia/Kolkata"),

    schedule="@daily",
    catchup=False,
    tags=["feature-store"],

    
) as dag:
    update_feature_store_task = PythonOperator(
        
        task_id="update_feature_store",
        python_callable=run_behaviour_feature_pipeline,
    )
