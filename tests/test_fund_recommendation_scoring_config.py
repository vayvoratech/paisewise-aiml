from __future__ import annotations

import pytest

from app.services.fund_recommendation_scoring_config import (
    FundRecommendationScoringConfigProvider,
)


def _set_valid_environment(monkeypatch):
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_RETURN_WEIGHT",
        "0.35",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_COST_WEIGHT",
        "0.25",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_SIZE_WEIGHT",
        "0.40",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_RETURN_LOWER_BOUND",
        "0.0",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_RETURN_UPPER_BOUND",
        "20.0",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_EXPENSE_RATIO_LOWER_BOUND",
        "0.0",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_EXPENSE_RATIO_UPPER_BOUND",
        "3.0",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_UNKNOWN_COST_SCORE",
        "0.5",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_UNKNOWN_SIZE_SCORE",
        "0.5",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_SIZE_LOG_DIVISOR",
        "10.0",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_STRONG_RETURN_THRESHOLD",
        "12.0",
    )
    monkeypatch.setenv(
        "FUND_RECOMMENDATION_LOW_COST_THRESHOLD",
        "1.0",
    )


def test_loads_configuration_from_environment(monkeypatch):
    _set_valid_environment(monkeypatch)

    config = FundRecommendationScoringConfigProvider.load()

    assert config.return_weight == 0.35
    assert config.cost_weight == 0.25
    assert config.size_weight == 0.40

    assert config.return_lower_bound == 0.0
    assert config.return_upper_bound == 20.0

    assert config.expense_ratio_lower_bound == 0.0
    assert config.expense_ratio_upper_bound == 3.0

    assert config.unknown_cost_score == 0.5
    assert config.unknown_size_score == 0.5

    assert config.size_log_divisor == 10.0
    assert config.strong_return_threshold == 12.0
    assert config.low_cost_threshold == 1.0


def test_missing_required_configuration_fails(monkeypatch):
    _set_valid_environment(monkeypatch)

    monkeypatch.delenv(
        "FUND_RECOMMENDATION_RETURN_WEIGHT",
    )

    with pytest.raises(
        RuntimeError,
        match="FUND_RECOMMENDATION_RETURN_WEIGHT",
    ):
        FundRecommendationScoringConfigProvider.load()


def test_invalid_numeric_configuration_fails(monkeypatch):
    _set_valid_environment(monkeypatch)

    monkeypatch.setenv(
        "FUND_RECOMMENDATION_RETURN_WEIGHT",
        "invalid",
    )

    with pytest.raises(
        RuntimeError,
        match="FUND_RECOMMENDATION_RETURN_WEIGHT",
    ):
        FundRecommendationScoringConfigProvider.load()


def test_empty_required_configuration_fails(monkeypatch):
    _set_valid_environment(monkeypatch)

    monkeypatch.setenv(
        "FUND_RECOMMENDATION_COST_WEIGHT",
        "   ",
    )

    with pytest.raises(
        RuntimeError,
        match="FUND_RECOMMENDATION_COST_WEIGHT",
    ):
        FundRecommendationScoringConfigProvider.load()


def test_invalid_cost_configuration_fails(monkeypatch):
    _set_valid_environment(monkeypatch)

    monkeypatch.setenv(
        "FUND_RECOMMENDATION_EXPENSE_RATIO_UPPER_BOUND",
        "invalid",
    )

    with pytest.raises(
        RuntimeError,
        match="FUND_RECOMMENDATION_EXPENSE_RATIO_UPPER_BOUND",
    ):
        FundRecommendationScoringConfigProvider.load()