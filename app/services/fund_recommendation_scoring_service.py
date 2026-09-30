from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FundRecommendationScoringConfig:
    return_weight: float
    cost_weight: float
    size_weight: float

    return_lower_bound: float
    return_upper_bound: float

    expense_ratio_lower_bound: float
    expense_ratio_upper_bound: float
    unknown_cost_score: float

    unknown_size_score: float
    size_log_divisor: float

    strong_return_threshold: float
    low_cost_threshold: float


class FundRecommendationScoringService:
    """
    Scores mutual-fund schemes using available catalog signals.

    Risk-o-Meter is intentionally not used by the current
    recommendation scoring flow. The database may retain a nullable
    risk_level field for future enrichment from an approved provider.

    This service is database-independent. It receives fund records from
    the repository and returns ranked recommendation candidates.

    All business scoring configuration is supplied through the config
    object. Configuration loading is intentionally handled outside this
    service.

    Collaborative filtering, diversity enforcement, exposure persistence,
    and API handling are handled by separate components.
    """

    _REQUIRED_FIELDS = (
        "scheme_code",
        "scheme_name",
        "amc_name",
        "category",
    )

    def __init__(
        self,
        config: FundRecommendationScoringConfig,
    ) -> None:
        self._config = config
        self._validate_config()

    def score_funds(
        self,
        funds: list[dict[str, Any]],
        *,
        goal: str | None = None,
        level: str | None = None,
    ) -> list[dict[str, Any]]:
        """Score and rank mutual funds."""

        if not funds:
            return []

        normalized_goal = self._normalize(goal)
        normalized_level = self._normalize(level)

        scored: list[dict[str, Any]] = []

        for fund in funds:
            self._validate_fund(fund)

            components = {
                "return": self._return_score(fund),
                "cost": self._cost_score(fund),
                "size": self._size_score(fund),
            }

            score = self._weighted_score(components)

            scored.append(
                {
                    "scheme_code": fund["scheme_code"],
                    "scheme_name": fund["scheme_name"],
                    "amc_name": fund["amc_name"],
                    "category": fund["category"],
                    "score": score,
                    "explanation": self._build_explanation(
                        fund=fund,
                        components=components,
                        goal=normalized_goal,
                        level=normalized_level,
                    ),
                }
            )

        scored.sort(
            key=lambda item: (
                -item["score"],
                item["scheme_name"].lower(),
            )
        )

        return scored

    def _validate_config(self) -> None:
        config = self._config

        weights = (
            config.return_weight,
            config.cost_weight,
            config.size_weight,
        )

        if any(weight < 0 for weight in weights):
            raise ValueError(
                "Recommendation score weights cannot be negative"
            )

        if sum(weights) <= 0:
            raise ValueError(
                "Recommendation score weights must have a positive total"
            )

        if config.return_lower_bound == config.return_upper_bound:
            raise ValueError(
                "Return score bounds must not be equal"
            )

        if (
            config.expense_ratio_lower_bound
            == config.expense_ratio_upper_bound
        ):
            raise ValueError(
                "Expense-ratio score bounds must not be equal"
            )

        if config.size_log_divisor <= 0:
            raise ValueError(
                "Size logarithmic divisor must be greater than zero"
            )

        if not 0.0 <= config.unknown_cost_score <= 1.0:
            raise ValueError(
                "Unknown cost score must be between 0 and 1"
            )

        if not 0.0 <= config.unknown_size_score <= 1.0:
            raise ValueError(
                "Unknown size score must be between 0 and 1"
            )

        if not 0.0 <= config.strong_return_threshold <= 1.0:
            raise ValueError(
                "Strong return threshold must be between 0 and 1"
            )

        if not 0.0 <= config.low_cost_threshold <= 1.0:
            raise ValueError(
                "Low cost threshold must be between 0 and 1"
            )

    @classmethod
    def _validate_fund(
        cls,
        fund: dict[str, Any],
    ) -> None:
        if not isinstance(fund, dict):
            raise ValueError(
                "Each fund must be a dictionary"
            )

        missing = [
            field
            for field in cls._REQUIRED_FIELDS
            if fund.get(field) in (None, "")
        ]

        if missing:
            raise ValueError(
                "Fund is missing required fields: "
                + ", ".join(missing)
            )

    @staticmethod
    def _normalize(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip().lower()

        return normalized or None

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float | None:
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _return_score(
        self,
        fund: dict[str, Any],
    ) -> float:
        values = [
            self._safe_float(fund.get("returns_1y")),
            self._safe_float(fund.get("returns_3y")),
            self._safe_float(fund.get("returns_5y")),
        ]

        available = [
            value
            for value in values
            if value is not None
        ]

        if not available:
            return 0.0

        average_return = sum(available) / len(available)

        return self._normalize_numeric(
            average_return,
            lower=self._config.return_lower_bound,
            upper=self._config.return_upper_bound,
        )

    def _cost_score(
        self,
        fund: dict[str, Any],
    ) -> float:
        expense_ratio = self._safe_float(
            fund.get("expense_ratio")
        )

        if expense_ratio is None:
            return self._config.unknown_cost_score

        return self._normalize_numeric(
            expense_ratio,
            lower=self._config.expense_ratio_lower_bound,
            upper=self._config.expense_ratio_upper_bound,
        )

    def _size_score(
        self,
        fund: dict[str, Any],
    ) -> float:
        fund_size = self._safe_float(
            fund.get("fund_size_cr")
        )

        if fund_size is None or fund_size <= 0:
            return self._config.unknown_size_score

        return min(
            1.0,
            math.log10(fund_size + 1)
            / self._config.size_log_divisor,
        )

    @staticmethod
    def _normalize_numeric(
        value: float,
        *,
        lower: float,
        upper: float,
    ) -> float:
        if lower == upper:
            return 0.5

        minimum = min(lower, upper)
        maximum = max(lower, upper)

        bounded = max(
            minimum,
            min(maximum, value),
        )

        normalized = (
            (bounded - minimum)
            / (maximum - minimum)
        )

        if lower > upper:
            normalized = 1.0 - normalized

        return round(
            normalized,
            6,
        )

    def _weighted_score(
        self,
        components: dict[str, float],
    ) -> float:
        weights = {
            "return": self._config.return_weight,
            "cost": self._config.cost_weight,
            "size": self._config.size_weight,
        }

        total_weight = sum(weights.values())

        if total_weight <= 0:
            raise ValueError(
                "Recommendation score weights "
                "must have a positive total"
            )

        score = sum(
            components[name] * weights[name]
            for name in weights
        )

        return round(
            score / total_weight,
            6,
        )

    def _build_explanation(
        self,
        *,
        fund: dict[str, Any],
        components: dict[str, float],
        goal: str | None,
        level: str | None,
    ) -> str:
        reasons: list[str] = []

        if (
            components["return"]
            >= self._config.strong_return_threshold
        ):
            reasons.append(
                "historical returns are relatively strong"
            )

        if (
            components["cost"]
            >= self._config.low_cost_threshold
        ):
            reasons.append(
                "the expense ratio is relatively low"
            )

        if level:
            reasons.append(
                f"the recommendation considers "
                f"learner level {level}"
            )

        if goal:
            reasons.append(
                f"the recommendation considers "
                f"the stated goal of {goal}"
            )

        if not reasons:
            reasons.append(
                "the fund matches the available "
                "catalog signals"
            )

        return (
            f"{fund['scheme_name']} is recommended "
            f"because "
            + "; ".join(reasons)
            + "."
        )