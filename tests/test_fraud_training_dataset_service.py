import pytest

from app.services.fraud_training_dataset_service import (
    FraudTrainingDatasetService,
)


ORDER = {
    "id": "order-1",
    "shares": 10,
    "price_per_share": 2500.0,
    "total_amount": 25000.0,
    "side": "BUY",
    "order_type": "MARKET",
}

TRUE_FRAUD_CASE = {
    "id": "case-1",
    "order_id": "order-1",
    "reviewer_decision": "TRUE_FRAUD",
}

FALSE_POSITIVE_CASE = {
    "id": "case-2",
    "order_id": "order-1",
    "reviewer_decision": "FALSE_POSITIVE",
}


def test_true_fraud_becomes_label_one():
    record = FraudTrainingDatasetService.build_record(
        TRUE_FRAUD_CASE,
        ORDER,
    )

    assert record["fraud_label"] == 1
    assert record["order_id"] == "order-1"


def test_false_positive_becomes_label_zero():
    record = FraudTrainingDatasetService.build_record(
        FALSE_POSITIVE_CASE,
        ORDER,
    )

    assert record["fraud_label"] == 0


def test_pending_case_is_rejected():
    case = {
        "id": "case-3",
        "order_id": "order-1",
        "reviewer_decision": None,
    }

    with pytest.raises(ValueError):
        FraudTrainingDatasetService.build_record(
            case,
            ORDER,
        )


def test_unknown_decision_is_rejected():
    case = {
        "id": "case-4",
        "order_id": "order-1",
        "reviewer_decision": "UNKNOWN",
    }

    with pytest.raises(ValueError):
        FraudTrainingDatasetService.build_record(
            case,
            ORDER,
        )


def test_dataset_builds_multiple_records():
    cases = [
        TRUE_FRAUD_CASE,
        FALSE_POSITIVE_CASE,
    ]

    orders = {
        "order-1": ORDER,
    }

    dataset = FraudTrainingDatasetService.build_dataset(
        cases,
        orders,
    )

    assert len(dataset) == 2
    assert dataset[0]["fraud_label"] == 1
    assert dataset[1]["fraud_label"] == 0


def test_missing_order_is_rejected():
    with pytest.raises(ValueError):
        FraudTrainingDatasetService.build_dataset(
            [TRUE_FRAUD_CASE],
            {},
        )