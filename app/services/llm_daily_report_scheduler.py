import os

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.llm_daily_report_service import LLMDailyReportService
from app.services.slack_notification_service import SlackNotificationService


class LLMDailyReportScheduler:
    """Schedules the daily LLM cost and performance report."""

    def __init__(
        self,
        report_service: LLMDailyReportService,
        hour: int | None = None,
        minute: int | None = None,
    ) -> None:
        self.hour = self._get_schedule_value(
            value=hour,
            environment_variable="LLM_DAILY_REPORT_HOUR",
            default=9,
        )

        self.minute = self._get_schedule_value(
            value=minute,
            environment_variable="LLM_DAILY_REPORT_MINUTE",
            default=0,
        )

        if not 0 <= self.hour <= 23:
            raise ValueError("hour must be between 0 and 23")

        if not 0 <= self.minute <= 59:
            raise ValueError("minute must be between 0 and 59")

        self.report_service = report_service
        self.scheduler = BackgroundScheduler()

    @staticmethod
    def _get_schedule_value(
        value: int | None,
        environment_variable: str,
        default: int,
    ) -> int:
        """Return an explicit value, environment value, or configured default."""

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

    def send_daily_report(self) -> None:
        """Generate and send the daily report."""

        report = self.report_service.generate_report()

        slack_service = SlackNotificationService()
        slack_service.notify(report)

    def start(self) -> None:
        """Register and start the daily report scheduler."""

        self.scheduler.add_job(
            self.send_daily_report,
            trigger="cron",
            hour=self.hour,
            minute=self.minute,
            id="llm_daily_report",
            replace_existing=True,
        )

        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        """Stop the scheduler."""

        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)