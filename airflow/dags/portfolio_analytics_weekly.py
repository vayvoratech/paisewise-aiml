import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator # type: ignore

from app.repositories.holdings_repository import (
    HoldingsRepository,
)
from app.services.portfolio_analytics_snapshot_service import (
    PortfolioAnalyticsSnapshotService,
)


def generate_weekly_portfolio_analytics() -> None:
    holdings_repository = HoldingsRepository()
    snapshot_service = PortfolioAnalyticsSnapshotService()

    user_ids = (
        holdings_repository
        .get_users_with_more_than_two_holdings()
    )

    for user_id in user_ids:
        snapshot_service.create_snapshot(
            user_id=user_id,
        )


with DAG(
    dag_id="portfolio_analytics_weekly",
    start_date=datetime(2026, 9, 3),
    schedule="0 0 * * 0",
    catchup=False,
    tags=["paisewise", "task4", "portfolio"],
) as dag:

    generate_analytics = PythonOperator(
        task_id="generate_weekly_portfolio_analytics",
        python_callable=(
            generate_weekly_portfolio_analytics
        ),
    )