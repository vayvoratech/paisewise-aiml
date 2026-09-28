from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


CASE_ID = "11111111-1111-1111-1111-111111111111"
ORDER_ID = "22222222-2222-2222-2222-222222222222"


def _pending_case():
    return {
        "id": CASE_ID,
        "order_id": ORDER_ID,
        "fraud_score": 0.85,
        "status": "PENDING_REVIEW",
        "reviewer_decision": None,
    }


def _updated_case(decision):
    return {
        "id": CASE_ID,
        "order_id": ORDER_ID,
        "fraud_score": 0.85,
        "status": decision,
        "reviewer_decision": decision,
    }


def test_case_not_found_returns_404():
    with patch(
        "app.api.routes.fraud_cases.FraudCaseRepository"
    ) as repository_class:
        repository = MagicMock()
        repository.get_case.return_value = None
        repository_class.return_value = repository

        response = client.post(
            f"/fraud/cases/{CASE_ID}/decision",
            json={"decision": "TRUE_FRAUD"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Fraud case not found"


def test_already_reviewed_case_returns_409():
    with patch(
        "app.api.routes.fraud_cases.FraudCaseRepository"
    ) as repository_class:
        repository = MagicMock()
        repository.get_case.return_value = _updated_case("TRUE_FRAUD")
        repository_class.return_value = repository

        response = client.post(
            f"/fraud/cases/{CASE_ID}/decision",
            json={"decision": "FALSE_POSITIVE"},
        )

    assert response.status_code == 409
    assert "already been reviewed" in response.json()["detail"]


def test_true_fraud_decision():
    with patch(
        "app.api.routes.fraud_cases.FraudCaseRepository"
    ) as repository_class:
        repository = MagicMock()
        repository.get_case.return_value = _pending_case()
        repository.update_reviewer_decision.return_value = (
            _updated_case("TRUE_FRAUD")
        )
        repository_class.return_value = repository

        response = client.post(
            f"/fraud/cases/{CASE_ID}/decision",
            json={"decision": "TRUE_FRAUD"},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == CASE_ID
    assert data["order_id"] == ORDER_ID
    assert data["decision"] == "TRUE_FRAUD"
    assert data["status"] == "TRUE_FRAUD"

    repository.update_reviewer_decision.assert_called_once_with(
        case_id=CASE_ID,
        decision="TRUE_FRAUD",
    )


def test_false_positive_decision():
    with patch(
        "app.api.routes.fraud_cases.FraudCaseRepository"
    ) as repository_class:
        repository = MagicMock()
        repository.get_case.return_value = _pending_case()
        repository.update_reviewer_decision.return_value = (
            _updated_case("FALSE_POSITIVE")
        )
        repository_class.return_value = repository

        response = client.post(
            f"/fraud/cases/{CASE_ID}/decision",
            json={"decision": "FALSE_POSITIVE"},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"] == "FALSE_POSITIVE"
    assert data["status"] == "FALSE_POSITIVE"


def test_invalid_decision_returns_422():
    response = client.post(
        f"/fraud/cases/{CASE_ID}/decision",
        json={"decision": "PENDING_REVIEW"},
    )

    assert response.status_code == 422