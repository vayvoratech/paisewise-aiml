import sys
from pathlib import Path

from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from app.pipelines.get_users import get_users
from app.pipelines.fetch_market_data import fetch_market_data


from app.pipelines.fetch_news import fetch_news
from app.services.call_ai_service import call_ai
from app.pipelines.save_portfolio_insight import save_portfolio_insight

from app.services.slack_service import (
    
    send_success_message,
    send_failure_message,
)


def get_users_task():
    users = get_users()

    print(f"Users with holdings: {len(users)}")

    for user in users:
        print(user)

    return users


def fetch_market_data_task():
    market_data = fetch_market_data()

    print("Market data:", market_data)

    return market_data


def fetch_news_task():
    news = fetch_news()

    print("News:", news)

    return news


def call_ai_task(**context):
    ti = context["ti"]

    users = ti.xcom_pull(task_ids="get_users")

    results = []

    for user in users:
        user_id = user["user_id"]

        print(f"Calling AI service for user: {user_id}")

        result = call_ai(
            user_id=user_id,
            language="English",
        )

        if result:
            results.append(
                {
                    "user_id": user_id,
                    "language": "English",
                    "result": result,
                }
            )

    print(f"AI results received: {len(results)}")

    return results


def save_insights_task(**context):
    ti = context["ti"]

    results = ti.xcom_pull(task_ids="call_ai_service")

    if not results:
        print("No AI results to save.")
        return

    saved = 0

    for item in results:
        user_id = item["user_id"]
        language = item["language"]
        result = item["result"]

        if isinstance(result, dict):
            insight = result.get("insight")

            if insight is None:
                insight = str(result)
        else:
            insight = str(result)

        save_portfolio_insight(
            user_id=user_id,
            insight=insight,
            language=language,
        )

        saved += 1

    print(f"Portfolio insights saved: {saved}")


def slack_success_callback(context):
    send_success_message()


def slack_failure_callback(context):
    error = context.get("exception")

    send_failure_message(error)


with DAG(
    dag_id="portfolio_insight_daily",
    start_date=datetime(2026, 8, 5),
    schedule="10 16 * * 1-5",
    catchup=False,
    tags=["portfolio"],
    on_success_callback=slack_success_callback,
    on_failure_callback=slack_failure_callback,
) as dag:

    users_task = PythonOperator(
        task_id="get_users",
        python_callable=get_users_task,
    )

    market_task = PythonOperator(
        task_id="fetch_market_data",
        python_callable=fetch_market_data_task,
    )

    news_task = PythonOperator(
        task_id="fetch_news",
        python_callable=fetch_news_task,
    )

    ai_task = PythonOperator(
        task_id="call_ai_service",
        python_callable=call_ai_task,
    )

    save_task = PythonOperator(
        task_id="save_portfolio_insight",
        python_callable=save_insights_task,
    )

    users_task >> [market_task, news_task] >> ai_task >> save_task