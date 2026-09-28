import os
from unittest.mock import MagicMock, patch

import pytest

from app.services.fund_recommendation_audit_scheduler import (
    FundRecommendationAuditScheduler,
)


def _report_service():
    return MagicMock()


def test_accepts_explicit_configuration():
    service = _report_service()

    scheduler = FundRecommendationAuditScheduler(
        report_service=service,
        day=15,
        hour=10,
        minute=30,
        concentration_threshold=0.70,
    )

    assert scheduler.day == 15
    assert scheduler.hour == 10
    assert scheduler.minute == 30
    assert scheduler.concentration_threshold == 0.70


def test_reads_configuration_from_environment():
    service = _report_service()

    with patch.dict(
        os.environ,
        {
            "FUND_RECOMMENDATION_AUDIT_DAY": "10",
            "FUND_RECOMMENDATION_AUDIT_HOUR": "8",
            "FUND_RECOMMENDATION_AUDIT_MINUTE": "15",
            "FUND_RECOMMENDATION_AUDIT_THRESHOLD": "0.65",
        },
        clear=False,
    ):
        scheduler = FundRecommendationAuditScheduler(
            report_service=service,
        )

    assert scheduler.day == 10
    assert scheduler.hour == 8
    assert scheduler.minute == 15
    assert scheduler.concentration_threshold == 0.65


def test_rejects_invalid_day():
    with pytest.raises(ValueError, match="day"):
        FundRecommendationAuditScheduler(
            report_service=_report_service(),
            day=0,
            concentration_threshold=0.70,
        )


def test_rejects_invalid_hour():
    with pytest.raises(ValueError, match="hour"):
        FundRecommendationAuditScheduler(
            report_service=_report_service(),
            hour=24,
            concentration_threshold=0.70,
        )


def test_rejects_invalid_minute():
    with pytest.raises(ValueError, match="minute"):
        FundRecommendationAuditScheduler(
            report_service=_report_service(),
            minute=60,
            concentration_threshold=0.70,
        )


def test_rejects_invalid_threshold():
    with pytest.raises(
        ValueError,
        match="concentration_threshold",
    ):
        FundRecommendationAuditScheduler(
            report_service=_report_service(),
            concentration_threshold=0.0,
        )


def test_requires_threshold_when_not_configured():
    with patch.dict(
        os.environ,
        {},
        clear=True,
    ):
        with pytest.raises(
            ValueError,
            match="FUND_RECOMMENDATION_AUDIT_THRESHOLD",
        ):
            FundRecommendationAuditScheduler(
                report_service=_report_service(),
            )


def test_run_audit_generates_report():
    service = _report_service()

    scheduler = FundRecommendationAuditScheduler(
        report_service=service,
        concentration_threshold=0.70,
    )

    scheduler.run_audit()

    service.generate.assert_called_once_with(
        concentration_threshold=0.70,
    )


def test_start_registers_monthly_job():
    service = _report_service()

    scheduler = FundRecommendationAuditScheduler(
        report_service=service,
        day=5,
        hour=9,
        minute=15,
        concentration_threshold=0.70,
    )

    scheduler.start()

    try:
        jobs = scheduler.scheduler.get_jobs()

        assert len(jobs) == 1
        assert (
            jobs[0].id
            == "fund_recommendation_monthly_audit"
        )
    finally:
        scheduler.shutdown()