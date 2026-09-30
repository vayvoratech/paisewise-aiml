import os

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.fraud_weekly_report_notification_service import (
    FraudWeeklyReportNotificationService,
)


class FraudWeeklyReportScheduler:
    """Schedules the weekly fraud summary report."""

    DAY_OF_WEEK_MAP = {
        "monday": "0",
        "tuesday": "1",
        "wednesday": "2",
        "thursday": "3",
        "friday": "4",
        "saturday": "5",
        "sunday": "6",
    }

    def __init__(
        self,
        report_service: FraudWeeklyReportNotificationService,
        day_of_week: str | None = None,
        hour: int | None = None,
        minute: int | None = None,
    ) -> None:
        configured_day = (
            day_of_week
            if day_of_week is not None
            else os.getenv(
                "FRAUD_WEEKLY_REPORT_DAY",
                "monday",
            )
        )

        self.day_of_week = configured_day.strip().lower()

        self.hour = self._get_schedule_value(
            value=hour,
            environment_variable="FRAUD_WEEKLY_REPORT_HOUR",
            default=9,
        )

        self.minute = self._get_schedule_value(
            value=minute,
            environment_variable="FRAUD_WEEKLY_REPORT_MINUTE",
            default=0,
        )

        if not self.day_of_week:
            raise ValueError(
                "day_of_week cannot be empty"
            )

        if self.day_of_week not in self.DAY_OF_WEEK_MAP:
            raise ValueError(
                "day_of_week must be a valid weekday name"
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
        """Return an explicit value, environment value, or default."""

        if value is not None:
            return value

        configured_value = os.getenv(environment_variable)

        if configured_value is None:
            return default

        try:
            return int(configured_value)
        except ValueError as exc:
            raise ValueError(
                f"{environment_variable} must be an integer"
            ) from exc

    def send_weekly_report(self) -> None:
        """Generate and send the weekly fraud report."""

        self.report_service.send()

    def start(self) -> None:
        """Register and start the weekly report scheduler."""

        self.scheduler.add_job(
            self.send_weekly_report,
            trigger="cron",
            day_of_week=self.DAY_OF_WEEK_MAP[self.day_of_week],
            hour=self.hour,
            minute=self.minute,
            id="fraud_weekly_report",
            replace_existing=True,
        )

        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        """Stop the scheduler."""

        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)