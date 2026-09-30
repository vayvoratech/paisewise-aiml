from app.services.fraud_weekly_report_notification_service import (
    FraudWeeklyReportNotificationService,
)


def test_real_weekly_fraud_report_slack_delivery():
    service = FraudWeeklyReportNotificationService()

    summary = service.send()

    assert summary is not None