from datetime import datetime, timezone

import pytest

from app.services.fraud_weekly_summary_service import (
    FraudWeeklySummaryService,
)


END_DATE = datetime(
    2026,
    9,
    22,
    12,
    0,
    tzinfo=timezone.utc,
)


def test_build_weekly_summary():
    service = FraudWeeklySummaryService()

    fraud_cases = [
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
            "reviewer_decision": "TRUE_FRAUD",
        },
    ]

    summary = service.build_summary(
        fraud_cases,
        end_date=END_DATE,
    )

    assert summary.flagged_cases == 3
    assert summary.reviewed_cases == 3
    assert summary.true_fraud_cases == 2
    assert summary.false_positive_cases == 1

    assert summary.true_positive_rate == pytest.approx(
        2 / 3
    )


def test_cases_outside_week_are_excluded():
    service = FraudWeeklySummaryService()

    fraud_cases = [
        {
            "id": "old-case",
            "created_at": datetime(
                2026,
                9,
                10,
                tzinfo=timezone.utc,
            ),
            "reviewer_decision": "TRUE_FRAUD",
        },
        {
            "id": "current-case",
            "created_at": datetime(
                2026,
                9,
                20,
                tzinfo=timezone.utc,
            ),
            "reviewer_decision": "FALSE_POSITIVE",
        },
    ]

    summary = service.build_summary(
        fraud_cases,
        end_date=END_DATE,
    )

    assert summary.flagged_cases == 1
    assert summary.reviewed_cases == 1
    assert summary.true_fraud_cases == 0
    assert summary.false_positive_cases == 1
    assert summary.true_positive_rate == 0.0


def test_unreviewed_cases_are_flagged_but_not_counted_as_reviewed():
    service = FraudWeeklySummaryService()

    fraud_cases = [
        {
            "id": "pending-case",
            "created_at": datetime(
                2026,
                9,
                20,
                tzinfo=timezone.utc,
            ),
            "reviewer_decision": None,
        },
    ]

    summary = service.build_summary(
        fraud_cases,
        end_date=END_DATE,
    )

    assert summary.flagged_cases == 1
    assert summary.reviewed_cases == 0
    assert summary.true_fraud_cases == 0
    assert summary.false_positive_cases == 0
    assert summary.true_positive_rate is None


def test_missing_created_at_is_rejected():
    service = FraudWeeklySummaryService()

    fraud_cases = [
        {
            "id": "case-1",
            "reviewer_decision": "TRUE_FRAUD",
        },
    ]

    with pytest.raises(
        ValueError,
        match="created_at",
    ):
        service.build_summary(
            fraud_cases,
            end_date=END_DATE,
        )