import pytest
from pydantic import ValidationError

from app.schemas.fraud import (
    FraudScoreRequest,
    FraudScoreResponse,
)


def test_valid_fraud_score_request():
    request = FraudScoreRequest(
        order_id="ae55f1d8-e767-4b28-b6a9-2bbe5cf58c80"
    )

    assert request.order_id == (
        "ae55f1d8-e767-4b28-b6a9-2bbe5cf58c80"
    )


def test_empty_order_id_is_rejected():
    with pytest.raises(ValidationError):
        FraudScoreRequest(order_id="")


def test_valid_fraud_score_response():
    response = FraudScoreResponse(
        order_id="ae55f1d8-e767-4b28-b6a9-2bbe5cf58c80",
        fraud_probability=0.75,
        decision="REVIEW",
    )

    assert response.fraud_probability == 0.75
    assert response.decision == "REVIEW"


@pytest.mark.parametrize(
    "probability",
    [-0.01, 1.01],
)
def test_invalid_fraud_probability_is_rejected(probability):
    with pytest.raises(ValidationError):
        FraudScoreResponse(
            order_id="test-order",
            fraud_probability=probability,
            decision="REVIEW",
        )