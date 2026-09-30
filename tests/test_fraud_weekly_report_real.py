from datetime import datetime, timedelta, timezone

from app.repositories.fraud_weekly_summary_repository import (
    FraudWeeklySummaryRepository,
)
from app.services.fraud_weekly_report_service import (
    FraudWeeklyReportService,
)


def test_real_weekly_fraud_report():
    service = FraudWeeklyReportService(
        repository=FraudWeeklySummaryRepository(),
    )

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=7)

    report = service.generate(
        end_date=end_date,
    )

    print("\nWeekly Fraud Report")
    print("-------------------")
    print(f"Period: {start_date} -> {end_date}")
    print(f"Flagged cases: {report.flagged_cases}")
    print(f"Reviewed cases: {report.reviewed_cases}")
    print(f"True fraud cases: {report.true_fraud_cases}")
    print(f"False positives: {report.false_positive_cases}")
    print(
        "True-positive rate:",
        report.true_positive_rate,
    )

    assert report.flagged_cases >= 0
    assert report.reviewed_cases >= 0
    assert report.true_fraud_cases >= 0
    assert report.false_positive_cases >= 0

    assert (
        report.true_fraud_cases
        + report.false_positive_cases
        == report.reviewed_cases
    )

    if report.reviewed_cases == 0:
        assert report.true_positive_rate is None
    else:
        assert report.true_positive_rate is not None
        assert 0.0 <= report.true_positive_rate <= 1.0