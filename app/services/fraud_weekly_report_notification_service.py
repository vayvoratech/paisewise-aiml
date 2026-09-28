from app.services.fraud_weekly_report_formatter import (
    FraudWeeklyReportFormatter,
)
from app.services.fraud_weekly_report_service import (
    FraudWeeklyReportService,
)
from app.services.slack_notification_service import (
    SlackNotificationService,
)


class FraudWeeklyReportNotificationService:
    """Generates and sends the weekly fraud report to Slack."""

    def __init__(
        self,
        report_service: FraudWeeklyReportService | None = None,
        formatter: FraudWeeklyReportFormatter | None = None,
        notifier: SlackNotificationService | None = None,
    ):
        self._report_service = (
            report_service
            if report_service is not None
            else FraudWeeklyReportService()
        )

        self._formatter = (
            formatter
            if formatter is not None
            else FraudWeeklyReportFormatter()
        )

        self._notifier = (
            notifier
            if notifier is not None
            else SlackNotificationService()
        )

    def send(self):
        summary = self._report_service.generate()

        message = self._formatter.format(summary)

        self._notifier.notify(message)

        return summary