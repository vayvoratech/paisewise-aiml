import pytest

from app.services.fraud_decision_policy import (
    FraudDecision,
    FraudDecisionPolicy,
)


def create_policy():
    return FraudDecisionPolicy(
        review_threshold=0.50,
        block_threshold=0.80,
    )


def test_low_probability_is_allowed():
    policy = create_policy()

    assert (
        policy.decide(0.20)
        == FraudDecision.ALLOW
    )


def test_review_probability_returns_review():
    policy = create_policy()

    assert (
        policy.decide(0.60)
        == FraudDecision.REVIEW
    )


def test_block_probability_returns_block():
    policy = create_policy()

    assert (
        policy.decide(0.90)
        == FraudDecision.BLOCK
    )


def test_review_threshold_is_inclusive():
    policy = create_policy()

    assert (
        policy.decide(0.50)
        == FraudDecision.REVIEW
    )


def test_block_threshold_is_inclusive():
    policy = create_policy()

    assert (
        policy.decide(0.80)
        == FraudDecision.BLOCK
    )


@pytest.mark.parametrize(
    "review_threshold,block_threshold",
    [
        (-0.1, 0.8),
        (0.5, 1.1),
        (0.8, 0.5),
        (0.8, 0.8),
    ],
)
def test_invalid_thresholds_are_rejected(
    review_threshold,
    block_threshold,
):
    with pytest.raises(ValueError):
        FraudDecisionPolicy(
            review_threshold=review_threshold,
            block_threshold=block_threshold,
        )


@pytest.mark.parametrize(
    "probability",
    [-0.01, 1.01],
)
def test_invalid_probability_is_rejected(probability):
    policy = create_policy()

    with pytest.raises(
        ValueError,
        match="fraud_probability must be between 0 and 1",
    ):
        policy.decide(probability)