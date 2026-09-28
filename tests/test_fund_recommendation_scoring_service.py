import pytest

from app.services.fund_recommendation_scoring_service import (
    FundRecommendationScoringConfig,
    FundRecommendationScoringService,
)


@pytest.fixture
def scoring_config() -> FundRecommendationScoringConfig:
    return FundRecommendationScoringConfig(
        return_weight=0.35,
        cost_weight=0.20,
        size_weight=0.15,
        return_lower_bound=-20.0,
        return_upper_bound=30.0,
        expense_ratio_lower_bound=2.0,
        expense_ratio_upper_bound=0.0,
        unknown_cost_score=0.5,
        unknown_size_score=0.5,
        size_log_divisor=4.0,
        strong_return_threshold=0.60,
        low_cost_threshold=0.60,
    )


@pytest.fixture
def service(
    scoring_config: FundRecommendationScoringConfig,
) -> FundRecommendationScoringService:
    return FundRecommendationScoringService(
        config=scoring_config,
    )


def test_empty_catalog_returns_empty_list(
    service: FundRecommendationScoringService,
):
    result = service.score_funds([])

    assert result == []


def test_funds_are_ranked_by_score(
    service: FundRecommendationScoringService,
):
    funds = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Fund A",
            "amc_name": "AMC A",
            "category": "Equity",
            "returns_1y": 12.0,
            "returns_3y": 14.0,
            "returns_5y": 16.0,
            "expense_ratio": 0.5,
            "fund_size_cr": 1000,
        },
        {
            "scheme_code": "FUND002",
            "scheme_name": "Fund B",
            "amc_name": "AMC B",
            "category": "Equity",
            "returns_1y": 5.0,
            "returns_3y": 7.0,
            "returns_5y": 8.0,
            "expense_ratio": 1.8,
            "fund_size_cr": 100,
        },
    ]

    result = service.score_funds(funds)

    assert len(result) == 2
    assert result[0]["score"] >= result[1]["score"]
    assert result[0]["scheme_code"] == "FUND001"


def test_score_is_bounded(
    service: FundRecommendationScoringService,
):
    funds = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Fund A",
            "amc_name": "AMC A",
            "category": "Equity",
            "returns_1y": 100.0,
            "returns_3y": 100.0,
            "returns_5y": 100.0,
            "expense_ratio": 0.0,
            "fund_size_cr": 100000,
        }
    ]

    result = service.score_funds(funds)

    assert len(result) == 1
    assert 0.0 <= result[0]["score"] <= 1.0


def test_missing_optional_metrics_do_not_fail(
    service: FundRecommendationScoringService,
):
    funds = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Fund A",
            "amc_name": "AMC A",
            "category": "Equity",
        }
    ]

    result = service.score_funds(funds)

    assert len(result) == 1
    assert 0.0 <= result[0]["score"] <= 1.0


def test_risk_level_is_not_required(
    service: FundRecommendationScoringService,
):
    funds = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Fund A",
            "amc_name": "AMC A",
            "category": "Equity",
            "returns_1y": 12.0,
            "returns_3y": 14.0,
            "returns_5y": 16.0,
            "expense_ratio": 0.5,
            "fund_size_cr": 1000,
        }
    ]

    result = service.score_funds(funds)

    assert len(result) == 1
    assert "risk_level" not in result[0]


def test_missing_required_field_fails(
    service: FundRecommendationScoringService,
):
    funds = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Fund A",
            "amc_name": "AMC A",
        }
    ]

    with pytest.raises(
        ValueError,
        match="Fund is missing required fields",
    ):
        service.score_funds(funds)


def test_explanation_is_generated(
    service: FundRecommendationScoringService,
):
    funds = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Fund A",
            "amc_name": "AMC A",
            "category": "Equity",
            "returns_1y": 12.0,
            "returns_3y": 14.0,
            "returns_5y": 16.0,
            "expense_ratio": 0.5,
            "fund_size_cr": 1000,
        }
    ]

    result = service.score_funds(
        funds,
        goal="retirement",
        level="beginner",
    )

    assert len(result) == 1
    assert "Fund A" in result[0]["explanation"]
    assert "retirement" in result[0]["explanation"]
    assert "beginner" in result[0]["explanation"]
    assert "risk profile" not in result[0]["explanation"].lower()