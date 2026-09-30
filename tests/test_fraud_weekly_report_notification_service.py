from unittest.mock import MagicMock

from app.services.fraud_weekly_report_notification_service import (
    FraudWeeklyReportNotificationService,
)
from app.services.fraud_weekly_summary_service import (
    FraudWeeklySummary,
)


def test_send_generates_formats_and_sends_report():
    report_service = MagicMock()
    formatter = MagicMock()
    notifier = MagicMock()

    summary = MagicMock(spec=FraudWeeklySummary)

    report_service.generate.return_value = summary
    formatter.format.return_value = "Weekly Fraud Summary"

    service = FraudWeeklyReportNotificationService(
        report_service=report_service,
        formatter=formatter,
        notifier=notifier,
    )

    result = service.send()

    assert result is summary

    report_service.generate.assert_called_once_with()
    formatter.format.assert_called_once_with(summary)
    notifier.notify.assert_called_once_with(
        "Weekly Fraud Summary"
    )


def test_send_does_not_send_when_report_generation_fails():
    report_service = MagicMock()
    formatter = MagicMock()
    notifier = MagicMock()

    report_service.generate.side_effect = RuntimeError(
        "Unable to generate report"
    )

    service = FraudWeeklyReportNotificationService(
        report_service=report_service,
        formatter=formatter,
        notifier=notifier,
    )

    try:
        service.send()
    except RuntimeError as exc:
        assert str(exc) == "Unable to generate report"
    else:
        raise AssertionError(
            "Expected report generation failure"
        )

    formatter.format.assert_not_called()
    notifier.notify.assert_not_called()