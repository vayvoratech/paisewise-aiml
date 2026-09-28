from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.repositories.recommendation_exposure_repository import (
    RecommendationExposureRepository,
)
from app.services.fund_recommendation_audit_service import (
    FundRecommendationAuditService,
)


class FundRecommendationAuditReportService:
    """Builds the monthly AMC recommendation audit."""

    def __init__(
        self,
        repository: (
            RecommendationExposureRepository | None
        ) = None,
        audit_service: (
            FundRecommendationAuditService | None
        ) = None,
    ) -> None:
        self._repository = (
            repository
            if repository is not None
            else RecommendationExposureRepository()
        )

        self._audit_service = (
            audit_service
            if audit_service is not None
            else FundRecommendationAuditService()
        )

    def generate(
        self,
        *,
        end_date: datetime | None = None,
        concentration_threshold: float,
    ) -> dict[str, Any]:
        """
        Generate an AMC concentration audit for the
        preceding month-long reporting window.
        """

        if end_date is None:
            end_date = datetime.now(timezone.utc)

        if end_date.tzinfo is None:
            end_date = end_date.replace(
                tzinfo=timezone.utc
            )

        start_date = end_date - timedelta(days=30)

        amc_exposure = (
            self._repository.get_monthly_amc_exposure(
                month_start=start_date,
                month_end=end_date,
            )
        )

        audit = self._audit_service.audit_month(
            amc_exposure,
            concentration_threshold=(
                concentration_threshold
            ),
        )

        return {
            "period_start": start_date,
            "period_end": end_date,
            **audit,
        }