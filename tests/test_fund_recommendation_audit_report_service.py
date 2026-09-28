from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.services.fund_recommendation_audit_report_service import (
    FundRecommendationAuditReportService,
)


def test_generates_monthly_audit():
    repository = MagicMock()
    audit_service = MagicMock()

    repository.get_monthly_amc_exposure.return_value = [
        {
            "amc_name": "AMC A",
            "exposure_count": 60,
            "unique_user_count": 10,
            "unique_scheme_count": 3,
        }
    ]

    audit_service.audit_month.return_value = {
        "total_exposures": 60,
        "amc_count": 1,
        "audited": True,
        "flagged_amcs": [],
        "amc_results": [],
    }

    service = FundRecommendationAuditReportService(
        repository=repository,
        audit_service=audit_service,
    )

    end_date = datetime(
        2026,
        9,
        23,
        tzinfo=timezone.utc,
    )

    result = service.generate(
        end_date=end_date,
        concentration_threshold=0.70,
    )

    assert result["period_end"] == end_date
    assert result["period_start"] == datetime(
        2026,
        8,
        24,
        tzinfo=timezone.utc,
    )

    assert result["total_exposures"] == 60
    assert result["audited"] is True

    repository.get_monthly_amc_exposure.assert_called_once_with(
        month_start=datetime(
            2026,
            8,
            24,
            tzinfo=timezone.utc,
        ),
        month_end=end_date,
    )

    audit_service.audit_month.assert_called_once_with(
        [
            {
                "amc_name": "AMC A",
                "exposure_count": 60,
                "unique_user_count": 10,
                "unique_scheme_count": 3,
            }
        ],
        concentration_threshold=0.70,
    )


def test_uses_current_time_when_end_date_missing():
    repository = MagicMock()
    audit_service = MagicMock()

    repository.get_monthly_amc_exposure.return_value = []

    audit_service.audit_month.return_value = {
        "total_exposures": 0,
        "amc_count": 0,
        "audited": False,
        "flagged_amcs": [],
        "amc_results": [],
    }

    service = FundRecommendationAuditReportService(
        repository=repository,
        audit_service=audit_service,
    )

    result = service.generate(
        concentration_threshold=0.70,
    )

    assert result["period_end"] is not None
    assert result["period_start"] is not None
    assert result["period_start"] < result["period_end"]


def test_naive_end_date_is_treated_as_utc():
    repository = MagicMock()
    audit_service = MagicMock()

    repository.get_monthly_amc_exposure.return_value = []

    audit_service.audit_month.return_value = {
        "total_exposures": 0,
        "amc_count": 0,
        "audited": False,
        "flagged_amcs": [],
        "amc_results": [],
    }

    service = FundRecommendationAuditReportService(
        repository=repository,
        audit_service=audit_service,
    )

    end_date = datetime(
        2026,
        9,
        23,
    )

    result = service.generate(
        end_date=end_date,
        concentration_threshold=0.70,
    )

    assert result["period_end"].tzinfo == timezone.utc


def test_report_preserves_audit_results():
    repository = MagicMock()
    audit_service = MagicMock()

    repository.get_monthly_amc_exposure.return_value = []

    expected_audit = {
        "total_exposures": 100,
        "amc_count": 2,
        "audited": True,
        "flagged_amcs": ["AMC A"],
        "amc_results": [
            {
                "amc_name": "AMC A",
                "exposure_count": 80,
                "unique_user_count": 20,
                "unique_scheme_count": 4,
                "exposure_share": 0.80,
                "concentration_flag": True,
            }
        ],
    }

    audit_service.audit_month.return_value = expected_audit

    service = FundRecommendationAuditReportService(
        repository=repository,
        audit_service=audit_service,
    )

    result = service.generate(
        end_date=datetime(
            2026,
            9,
            23,
            tzinfo=timezone.utc,
        ),
        concentration_threshold=0.70,
    )

    assert result["total_exposures"] == 100
    assert result["flagged_amcs"] == ["AMC A"]
    assert result["amc_results"] == expected_audit[
        "amc_results"
    ]