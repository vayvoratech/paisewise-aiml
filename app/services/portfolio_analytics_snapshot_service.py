from datetime import date
from typing import Any

from app.repositories.portfolio_analytics_repository import (
    PortfolioAnalyticsRepository,
)
from app.services.portfolio_analytics_service import (
    PortfolioAnalyticsService,
)


class PortfolioAnalyticsSnapshotService:
    """
    Creates and stores portfolio analytics snapshots
    in PostgreSQL.
    """

    def __init__(
        self,
        analytics_service: (
            PortfolioAnalyticsService | None
        ) = None,
        repository: (
            PortfolioAnalyticsRepository | None
        ) = None,
    ) -> None:
        self.analytics_service = (
            analytics_service
            or PortfolioAnalyticsService()
        )

        self.repository = (
            repository
            or PortfolioAnalyticsRepository()
        )

    def create_snapshot(
        self,
        user_id: str,
        snapshot_date: date | None = None,
    ) -> None:
        if not user_id or not user_id.strip():
            raise ValueError(
                "user_id cannot be empty"
            )

        normalized_user_id = user_id.strip()

        analytics = self.analytics_service.calculate(
            user_id=normalized_user_id
        )

        analytics_data: dict[str, Any] = (
            analytics.model_dump()
        )

        snapshot_date = (
            snapshot_date or date.today()
        )

        self.repository.save_snapshot(
            user_id=normalized_user_id,
            snapshot_date=snapshot_date,
            analytics_data=analytics_data,
        )