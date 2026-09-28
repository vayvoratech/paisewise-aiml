import pytest

from app.services.fund_recommendation_audit_service import (
    FundRecommendationAuditService,
)


def test_empty_data_is_not_audited():
    service = FundRecommendationAuditService()

    result = service.audit_month(
        [],
        concentration_threshold=0.50,
    )

    assert result["total_exposures"] == 0
    assert result["amc_count"] == 0
    assert result["audited"] is False
    assert result["flagged_amcs"] == []


def test_calculates_amc_exposure_share():
    service = FundRecommendationAuditService()

    result = service.audit_month(
        [
            {
                "amc_name": "AMC A",
                "exposure_count": 60,
                "unique_user_count": 10,
                "unique_scheme_count": 3,
            },
            {
                "amc_name": "AMC B",
                "exposure_count": 40,
                "unique_user_count": 8,
                "unique_scheme_count": 4,
            },
        ],
        concentration_threshold=0.70,
    )

    assert result["total_exposures"] == 100
    assert result["amc_count"] == 2
    assert result["audited"] is True

    assert (
        result["amc_results"][0]["amc_name"]
        == "AMC A"
    )

    assert (
        result["amc_results"][0]["exposure_share"]
        == 0.60
    )


def test_flags_amc_above_threshold():
    service = FundRecommendationAuditService()

    result = service.audit_month(
        [
            {
                "amc_name": "AMC A",
                "exposure_count": 80,
                "unique_user_count": 20,
                "unique_scheme_count": 5,
            },
            {
                "amc_name": "AMC B",
                "exposure_count": 20,
                "unique_user_count": 10,
                "unique_scheme_count": 3,
            },
        ],
        concentration_threshold=0.70,
    )

    assert result["flagged_amcs"] == ["AMC A"]
    assert (
        result["amc_results"][0]["concentration_flag"]
        is True
    )


def test_equal_to_threshold_is_not_flagged():
    service = FundRecommendationAuditService()

    result = service.audit_month(
        [
            {
                "amc_name": "AMC A",
                "exposure_count": 50,
                "unique_user_count": 10,
                "unique_scheme_count": 2,
            },
            {
                "amc_name": "AMC B",
                "exposure_count": 50,
                "unique_user_count": 10,
                "unique_scheme_count": 2,
            },
        ],
        concentration_threshold=0.50,
    )

    assert result["flagged_amcs"] == []


def test_zero_exposures_are_not_audited():
    service = FundRecommendationAuditService()

    result = service.audit_month(
        [
            {
                "amc_name": "AMC A",
                "exposure_count": 0,
                "unique_user_count": 0,
                "unique_scheme_count": 0,
            }
        ],
        concentration_threshold=0.50,
    )

    assert result["audited"] is False
    assert result["total_exposures"] == 0
    assert (
        result["amc_results"][0]["exposure_share"]
        == 0.0
    )


def test_invalid_threshold_is_rejected():
    service = FundRecommendationAuditService()

    with pytest.raises(
        ValueError,
        match="concentration_threshold",
    ):
        service.audit_month(
            [],
            concentration_threshold=0.0,
        )


def test_negative_exposure_is_treated_as_zero():
    service = FundRecommendationAuditService()

    result = service.audit_month(
        [
            {
                "amc_name": "AMC A",
                "exposure_count": -10,
                "unique_user_count": -2,
                "unique_scheme_count": -1,
            }
        ],
        concentration_threshold=0.50,
    )

    assert result["total_exposures"] == 0
    assert result["audited"] is False