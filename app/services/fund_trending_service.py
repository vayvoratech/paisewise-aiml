from __future__ import annotations

from typing import Any

from app.repositories.fund_trending_repository import (
    FundTrendingRepository,
)


class FundTrendingService:
    """Builds learner-level trending mutual-fund results."""

    def __init__(
        self,
        repository: FundTrendingRepository | None = None,
    ) -> None:
        self.repository = (
            repository
            or FundTrendingRepository()
        )

    def get_trending(
        self,
        *,
        level: int,
        days: int = 28,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Return funds trending among users at the specified
        learner level.
        """

        if level < 1:
            raise ValueError(
                "level must be greater than zero"
            )

        if days <= 0:
            raise ValueError(
                "days must be greater than zero"
            )

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

        records = self.repository.get_trending_for_level(
            level,
            days=days,
            limit=limit,
        )

        return [
            {
                "schemeCode": record["scheme_code"],
                "schemeName": record["scheme_name"],
                "amcName": record["amc_name"],
                "learnerLevel": str(level),
                "exposureCount": int(
                    record["exposure_count"]
                ),
            }
            for record in records
        ]