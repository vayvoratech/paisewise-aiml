import pytest

from app.services.fraud_decision_policy import (
    FraudDecision,
    FraudDecisionPolicy,
)
from app.services.fraud_model_service import FraudModelService
from app.services.fraud_scoring_service import FraudScoringService # type: ignore


class FakeFraudModel:
    def __init__(self, probability):
        self.probability = probability

    def predict_proba(self, features):
        assert len(features) == 1
        assert len(features[0]) == 7

        return [[
            1.0 - self.probability,
            self.probability,
        ]]


def create_service(probability):
    model = FakeFraudModel(probability)

    model_service = FraudModelService(model)

    policy = FraudDecisionPolicy(
        review_threshold=0.50,
        block_threshold=0.80,
    )

    return FraudScoringService(
        model_service=model_service,
        decision_policy=policy,
    )


def create_order():
    return {
        "shares": 10,
        "price_per_share": 2500.0,
        "total_amount": 25000.0,
        "side": "BUY",
        "order_type": "MARKET",
    }


def test_low_risk_order_is_allowed():
    service = create_service(0.20)

    result = service.score_order(create_order())

    assert result.fraud_probability == 0.20
    assert result.decision == FraudDecision.ALLOW


def test_medium_risk_order_requires_review():
    service = create_service(0.60)

    result = service.score_order(create_order())

    assert result.fraud_probability == 0.60
    assert result.decision == FraudDecision.REVIEW


def test_high_risk_order_is_blocked():
    service = create_service(0.90)

    result = service.score_order(create_order())

    assert result.fraud_probability == 0.90
    assert result.decision == FraudDecision.BLOCK


def test_invalid_order_is_rejected():
    service = create_service(0.20)

    order = create_order()
    order["shares"] = 0

    with pytest.raises(
        ValueError,
        match="shares must be greater than zero",
    ):
        service.score_order(order)


def test_dependencies_are_required():
    policy = FraudDecisionPolicy(
        review_threshold=0.50,
        block_threshold=0.80,
    )

    model = FakeFraudModel(0.20)
    model_service = FraudModelService(model)

    with pytest.raises(
        ValueError,
        match="model_service cannot be None",
    ):
        FraudScoringService(
            model_service=None,
            decision_policy=policy,
        )

    with pytest.raises(
        ValueError,
        match="decision_policy cannot be None",
    ):
        FraudScoringService(
            model_service=model_service,
            decision_policy=None,
        )