from datetime import datetime, timezone

from app.services.fraud_weekly_report_formatter import (
    FraudWeeklyReportFormatter,
)
from app.services.fraud_weekly_summary_service import (
    FraudWeeklySummary,
)


def test_format_weekly_fraud_report():
    summary = FraudWeeklySummary(
        start_date=datetime(
            2026,
            9,
            15,
            tzinfo=timezone.utc,
        ),
        end_date=datetime(
            2026,
            9,
            22,
            tzinfo=timezone.utc,
        ),
        flagged_cases=10,
        reviewed_cases=8,
        true_fraud_cases=6,
        false_positive_cases=2,
        true_positive_rate=0.75,
    )

    formatter = FraudWeeklyReportFormatter()

    report = formatter.format(summary)

    assert "Weekly Fraud Summary" in report
    assert "Flagged cases: 10" in report
    assert "Reviewed cases: 8" in report
    assert "True fraud cases: 6" in report
    assert "False positives: 2" in report
    assert "True-positive rate: 75.00%" in report


def test_format_report_without_reviewed_cases():
    summary = FraudWeeklySummary(
        start_date=datetime(
            2026,
            9,
            15,
            tzinfo=timezone.utc,
        ),
        end_date=datetime(
            2026,
            9,
            22,
            tzinfo=timezone.utc,
        ),
        flagged_cases=2,
        reviewed_cases=0,
        true_fraud_cases=0,
        false_positive_cases=0,
        true_positive_rate=None,
    )

    formatter = FraudWeeklyReportFormatter()

    report = formatter.format(summary)

    assert "Flagged cases: 2" in report
    assert "Reviewed cases: 0" in report
    assert "True-positive rate: N/A" in report
    assert "None" not in report