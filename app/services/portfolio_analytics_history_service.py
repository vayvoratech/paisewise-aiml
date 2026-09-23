from datetime import date, datetime
from typing import Any

from app.repositories.portfolio_analytics_repository import (
    PortfolioAnalyticsRepository,
)
from app.schemas.portfolio_analytics_history import (
    PortfolioAnalyticsHistoryItem,
    PortfolioAnalyticsHistoryResponse,
)


class PortfolioAnalyticsHistoryService:
    """
    Retrieves historical portfolio analytics snapshots
    from PostgreSQL.
    """

    def __init__(
        self,
        repository: PortfolioAnalyticsRepository | None = None,
    ) -> None:
        self.repository = (
            repository
            or PortfolioAnalyticsRepository()
        )

    @staticmethod
    def _to_string(value: Any) -> str:
        if isinstance(value, (date, datetime)):
            return value.isoformat()

        return str(value)

    def get_history(
        self,
        user_id: str,
    ) -> PortfolioAnalyticsHistoryResponse:
        if not user_id or not user_id.strip():
            raise ValueError(
                "user_id cannot be empty"
            )

        normalized_user_id = user_id.strip()

        rows = self.repository.get_history(
            normalized_user_id
        )

        snapshots = [
            PortfolioAnalyticsHistoryItem(
                id=self._to_string(row["id"]),
                userId=self._to_string(
                    row["user_id"]
                ),
                snapshotDate=self._to_string(
                    row["snapshot_date"]
                ),
                analyticsData=row["analytics_data"],
                createdAt=self._to_string(
                    row["created_at"]
                ),
            )
            for row in rows
        ]

        return PortfolioAnalyticsHistoryResponse(
            userId=normalized_user_id,
            snapshots=snapshots,
        )