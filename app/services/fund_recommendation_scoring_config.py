from __future__ import annotations

import os

from app.services.fund_recommendation_scoring_service import (
    FundRecommendationScoringConfig,
)


class FundRecommendationScoringConfigProvider:
    """
    Loads mutual-fund recommendation scoring configuration from
    environment variables.

    No recommendation business values are embedded in the provider.
    Required configuration must be explicitly supplied through the
    environment.

    Risk-O-Meter configuration is intentionally not part of the
    current recommendation scoring flow. A future approved risk
    provider can be integrated independently without changing this
    configuration contract.
    """

    _ENV_NAMES = (
        "FUND_RECOMMENDATION_RETURN_WEIGHT",
        "FUND_RECOMMENDATION_COST_WEIGHT",
        "FUND_RECOMMENDATION_SIZE_WEIGHT",
        "FUND_RECOMMENDATION_RETURN_LOWER_BOUND",
        "FUND_RECOMMENDATION_RETURN_UPPER_BOUND",
        "FUND_RECOMMENDATION_EXPENSE_RATIO_LOWER_BOUND",
        "FUND_RECOMMENDATION_EXPENSE_RATIO_UPPER_BOUND",
        "FUND_RECOMMENDATION_UNKNOWN_COST_SCORE",
        "FUND_RECOMMENDATION_UNKNOWN_SIZE_SCORE",
        "FUND_RECOMMENDATION_SIZE_LOG_DIVISOR",
        "FUND_RECOMMENDATION_STRONG_RETURN_THRESHOLD",
        "FUND_RECOMMENDATION_LOW_COST_THRESHOLD",
    )

    @classmethod
    def load(cls) -> FundRecommendationScoringConfig:
        return FundRecommendationScoringConfig(
            return_weight=cls._float(
                "FUND_RECOMMENDATION_RETURN_WEIGHT"
            ),
            cost_weight=cls._float(
                "FUND_RECOMMENDATION_COST_WEIGHT"
            ),
            size_weight=cls._float(
                "FUND_RECOMMENDATION_SIZE_WEIGHT"
            ),
            return_lower_bound=cls._float(
                "FUND_RECOMMENDATION_RETURN_LOWER_BOUND"
            ),
            return_upper_bound=cls._float(
                "FUND_RECOMMENDATION_RETURN_UPPER_BOUND"
            ),
            expense_ratio_lower_bound=cls._float(
                "FUND_RECOMMENDATION_EXPENSE_RATIO_LOWER_BOUND"
            ),
            expense_ratio_upper_bound=cls._float(
                "FUND_RECOMMENDATION_EXPENSE_RATIO_UPPER_BOUND"
            ),
            unknown_cost_score=cls._float(
                "FUND_RECOMMENDATION_UNKNOWN_COST_SCORE"
            ),
            unknown_size_score=cls._float(
                "FUND_RECOMMENDATION_UNKNOWN_SIZE_SCORE"
            ),
            size_log_divisor=cls._float(
                "FUND_RECOMMENDATION_SIZE_LOG_DIVISOR"
            ),
            strong_return_threshold=cls._float(
                "FUND_RECOMMENDATION_STRONG_RETURN_THRESHOLD"
            ),
            low_cost_threshold=cls._float(
                "FUND_RECOMMENDATION_LOW_COST_THRESHOLD"
            ),
        )

    @classmethod
    def _required(cls, name: str) -> str:
        value = os.getenv(name)

        if value is None or not value.strip():
            raise RuntimeError(
                f"Required recommendation configuration "
                f"'{name}' is not configured"
            )

        return value.strip()

    @classmethod
    def _float(cls, name: str) -> float:
        value = cls._required(name)

        try:
            return float(value)
        except ValueError as exc:
            raise RuntimeError(
                f"Recommendation configuration '{name}' "
                f"must be a valid number"
            ) from exc