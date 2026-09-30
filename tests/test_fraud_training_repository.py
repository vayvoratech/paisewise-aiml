from app.repositories.fraud_training_repository import (
    FraudTrainingRepository,
)


def test_get_reviewed_cases_returns_list():
    repository = FraudTrainingRepository()

    cases = repository.get_reviewed_cases()

    assert isinstance(cases, list)


def test_reviewed_cases_have_required_fields():
    repository = FraudTrainingRepository()

    cases = repository.get_reviewed_cases()

    for case in cases:
        assert case["fraud_case_id"] is not None
        assert case["order_id"] is not None
        assert case["reviewer_decision"] in {
            "TRUE_FRAUD",
            "FALSE_POSITIVE",
        }
        assert case["shares"] > 0
        assert case["price_per_share"] > 0
        assert case["total_amount"] > 0
        assert case["side"] in {"BUY", "SELL"}
        assert case["order_type"] in {"MARKET", "LIMIT"}