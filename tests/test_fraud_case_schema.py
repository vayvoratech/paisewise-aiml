import pytest
from pydantic import ValidationError

from app.schemas.fraud_case import (
    FraudCaseDecisionRequest,
    FraudCaseDecisionResponse,
)


def test_true_fraud_decision_is_valid():
    request = FraudCaseDecisionRequest(
        decision="TRUE_FRAUD",
    )

    assert request.decision == "TRUE_FRAUD"


def test_false_positive_decision_is_valid():
    request = FraudCaseDecisionRequest(
        decision="FALSE_POSITIVE",
    )

    assert request.decision == "FALSE_POSITIVE"


def test_pending_review_is_rejected():
    with pytest.raises(ValidationError):
        FraudCaseDecisionRequest(
            decision="PENDING_REVIEW",
        )


def test_invalid_decision_is_rejected():
    with pytest.raises(ValidationError):
        FraudCaseDecisionRequest(
            decision="UNKNOWN",
        )


def test_response_schema():
    response = FraudCaseDecisionResponse(
        case_id="case-1",
        order_id="order-1",
        decision="FALSE_POSITIVE",
        status="FALSE_POSITIVE",
    )

    assert response.case_id == "case-1"
    assert response.order_id == "order-1"
    assert response.decision == "FALSE_POSITIVE"
    assert response.status == "FALSE_POSITIVE"