from datetime import datetime, timedelta, timezone

from app.repositories.fraud_weekly_summary_repository import (
    FraudWeeklySummaryRepository,
)
from app.services.fraud_weekly_summary_service import (
    FraudWeeklySummary,
    FraudWeeklySummaryService,
)


class FraudWeeklyReportService:
    """Builds the weekly fraud report from persisted fraud cases."""

    def __init__(
        self,
        repository: FraudWeeklySummaryRepository | None = None,
        summary_service: FraudWeeklySummaryService | None = None,
    ):
        self._repository = (
            repository
            if repository is not None
            else FraudWeeklySummaryRepository()
        )

        self._summary_service = (
            summary_service
            if summary_service is not None
            else FraudWeeklySummaryService()
        )

    def generate(
        self,
        *,
        end_date: datetime | None = None,
    ) -> FraudWeeklySummary:
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        start_date = end_date - timedelta(days=7)

        fraud_cases = self._repository.get_cases_between(
            start_date,
            end_date,
        )

        return self._summary_service.build_summary(
            fraud_cases,
            end_date=end_date,
        )