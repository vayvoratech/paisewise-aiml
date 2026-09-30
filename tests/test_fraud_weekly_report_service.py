from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.services.fraud_weekly_report_service import (
    FraudWeeklyReportService,
)


END_DATE = datetime(
    2026,
    9,
    22,
    12,
    0,
    tzinfo=timezone.utc,
)


def test_generate_builds_weekly_report():
    repository = MagicMock()

    repository.get_cases_between.return_value = [
        {
            "id": "case-1",
            "created_at": datetime(
                2026,
                9,
                20,
                tzinfo=timezone.utc,
            ),
            "reviewer_decision": "TRUE_FRAUD",
        },
        {
            "id": "case-2",
            "created_at": datetime(
                2026,
                9,
                19,
                tzinfo=timezone.utc,
            ),
            "reviewer_decision": "FALSE_POSITIVE",
        },
        {
            "id": "case-3",
            "created_at": datetime(
                2026,
                9,
                18,
                tzinfo=timezone.utc,
            ),
            "reviewer_decision": None,
        },
    ]

    service = FraudWeeklyReportService(
        repository=repository,
    )

    report = service.generate(
        end_date=END_DATE,
    )

    assert report.flagged_cases == 3
    assert report.reviewed_cases == 2
    assert report.true_fraud_cases == 1
    assert report.false_positive_cases == 1
    assert report.true_positive_rate == pytest.approx(0.5)

    repository.get_cases_between.assert_called_once()

    start_date, end_date = (
        repository.get_cases_between.call_args.args
    )

    assert end_date == END_DATE

    assert (
        end_date - start_date
    ).total_seconds() == 7 * 24 * 60 * 60


def test_generate_uses_current_time_when_end_date_not_provided():
    repository = MagicMock()
    repository.get_cases_between.return_value = []

    service = FraudWeeklyReportService(
        repository=repository,
    )

    before = datetime.now(timezone.utc)

    report = service.generate()

    after = datetime.now(timezone.utc)

    assert report.flagged_cases == 0
    assert report.reviewed_cases == 0
    assert report.true_fraud_cases == 0
    assert report.false_positive_cases == 0
    assert report.true_positive_rate is None

    start_date, end_date = (
        repository.get_cases_between.call_args.args
    )

    assert before <= end_date <= after
    assert (
        end_date - start_date
    ).total_seconds() == 7 * 24 * 60 * 60


def test_generate_accepts_naive_end_date():
    repository = MagicMock()
    repository.get_cases_between.return_value = []

    service = FraudWeeklyReportService(
        repository=repository,
    )

    naive_end_date = datetime(
        2026,
        9,
        22,
        12,
        0,
    )

    report = service.generate(
        end_date=naive_end_date,
    )

    assert report.flagged_cases == 0
    assert report.true_positive_rate is None

    _, end_date = (
        repository.get_cases_between.call_args.args
    )

    assert end_date.tzinfo == timezone.utc