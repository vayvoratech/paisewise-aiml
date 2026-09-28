from __future__ import annotations

import os

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.fund_recommendation_audit_report_service import (
    FundRecommendationAuditReportService,
)


class FundRecommendationAuditScheduler:
    """Schedules the monthly mutual-fund AMC recommendation audit."""

    def __init__(
        self,
        report_service: FundRecommendationAuditReportService,
        day: int | None = None,
        hour: int | None = None,
        minute: int | None = None,
        concentration_threshold: float | None = None,
    ) -> None:
        self.day = self._get_schedule_value(
            value=day,
            environment_variable=(
                "FUND_RECOMMENDATION_AUDIT_DAY"
            ),
            default=1,
        )

        self.hour = self._get_schedule_value(
            value=hour,
            environment_variable=(
                "FUND_RECOMMENDATION_AUDIT_HOUR"
            ),
            default=9,
        )

        self.minute = self._get_schedule_value(
            value=minute,
            environment_variable=(
                "FUND_RECOMMENDATION_AUDIT_MINUTE"
            ),
            default=0,
        )

        self.concentration_threshold = (
            self._get_threshold(
                concentration_threshold
            )
        )

        if not 1 <= self.day <= 31:
            raise ValueError(
                "day must be between 1 and 31"
            )

        if not 0 <= self.hour <= 23:
            raise ValueError(
                "hour must be between 0 and 23"
            )

        if not 0 <= self.minute <= 59:
            raise ValueError(
                "minute must be between 0 and 59"
            )

        self.report_service = report_service
        self.scheduler = BackgroundScheduler()

    @staticmethod
    def _get_schedule_value(
        value: int | None,
        environment_variable: str,
        default: int,
    ) -> int:
        """Return explicit value, environment value, or default."""

        if value is not None:
            return value

        configured_value = os.getenv(
            environment_variable
        )

        if configured_value is None:
            return default

        try:
            return int(configured_value)
        except ValueError as exc:
            raise ValueError(
                f"{environment_variable} must be an integer"
            ) from exc

    @staticmethod
    def _get_threshold(
        value: float | None,
    ) -> float:
        """Return explicit or environment-configured threshold."""

        if value is None:
            configured_value = os.getenv(
                "FUND_RECOMMENDATION_AUDIT_THRESHOLD"
            )

            if configured_value is None:
                raise ValueError(
                    "FUND_RECOMMENDATION_AUDIT_THRESHOLD "
                    "must be configured"
                )

            try:
                value = float(configured_value)
            except ValueError as exc:
                raise ValueError(
                    "FUND_RECOMMENDATION_AUDIT_THRESHOLD "
                    "must be a number"
                ) from exc

        if not 0.0 < value <= 1.0:
            raise ValueError(
                "concentration_threshold must be greater "
                "than zero and less than or equal to one"
            )

        return value

    def run_audit(self) -> None:
        """Generate the monthly AMC recommendation audit."""

        self.report_service.generate(
            concentration_threshold=(
                self.concentration_threshold
            )
        )

    def start(self) -> None:
        """Register and start the monthly audit scheduler."""

        self.scheduler.add_job(
            self.run_audit,
            trigger="cron",
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            id="fund_recommendation_monthly_audit",
            replace_existing=True,
        )

        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        """Stop the scheduler."""

        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)