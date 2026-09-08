import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator # type: ignore

from app.integrations.kafka_producer import KafkaProducerAdapter
from app.repositories.churn_reengagement_repository import (
    ChurnReengagementRepository,
)
from app.repositories.user_journey_repository import UserJourneyRepository
from app.services.churn_batch_service import ChurnBatchService
from app.services.churn_notification_service import ChurnNotificationService
from app.services.daily_reengagement_service import DailyReengagementService
from app.services.reengagement_campaign_service import (
    ReengagementCampaignService,
)
from app.services.reengagement_llm_service import ReengagementLLMService
from app.services.reengagement_message_service import (
    ReengagementMessageService,
)
from app.services.reengagement_notification_service import (
    ReengagementNotificationService,
)
from app.services.llm.gemini_provider import GeminiProvider


def calculate_daily_churn_scores(**context) -> None:
    logical_date = context["logical_date"]

    churn_batch_service = ChurnBatchService()

    results = (
        churn_batch_service.calculate_for_users_registered_seven_days_ago(
            today=logical_date.date()
        )
    )

    context["ti"].xcom_push(
        key="churn_results",
        value=[
            {
                "userId": result.userId,
                "score": result.score,
                "riskLevel": result.riskLevel,
            }
            for result in results
        ],
    )


def process_daily_reengagement_notifications(**context) -> None:
    churn_results = context["ti"].xcom_pull(
        task_ids="calculate_daily_churn_scores",
        key="churn_results",
    )

    if not churn_results:
        return

    from app.services.churn_service import ChurnResponse

    results = [
        ChurnResponse(
            userId=item["userId"],
            score=item["score"],
            riskLevel=item["riskLevel"],
        )
        for item in churn_results
    ]

    producer = KafkaProducerAdapter()

    try:
        kafka_notification_service = ChurnNotificationService(
            producer=producer,
        )

        template_service = ReengagementMessageService()

        llm_service = ReengagementLLMService(
            llm_provider=GeminiProvider(),
        )

        campaign_service = ReengagementCampaignService(
            template_service=template_service,
            llm_service=llm_service,
        )

        # Repository is explicitly provided for production/DAG execution.
        reengagement_repository = ChurnReengagementRepository()

        notification_service = ReengagementNotificationService(
            campaign_service=campaign_service,
            notification_service=kafka_notification_service,
            reengagement_repository=reengagement_repository,
        )

        journey_repository = UserJourneyRepository()

        daily_reengagement_service = DailyReengagementService(
            notification_service=notification_service,
            journey_repository=journey_repository,
        )

        asyncio.run(
            daily_reengagement_service.process(results)
        )

        producer.flush()

    finally:
        producer.close()


with DAG(
    dag_id="churn_score_daily",
    start_date=datetime(2026, 9, 8),
    schedule="0 9 * * *",
    catchup=False,
    tags=[
        "paisewise",
        "task5",
        "churn",
    ],
) as dag:

    calculate_churn = PythonOperator(
        task_id="calculate_daily_churn_scores",
        python_callable=calculate_daily_churn_scores,
    )

    process_reengagement = PythonOperator(
        task_id="process_daily_reengagement_notifications",
        python_callable=process_daily_reengagement_notifications,
    )

    calculate_churn >> process_reengagement