import pytest

from app.services.fraud_training_data_quality_service import (
    FraudTrainingDataQualityService,
)


def make_cases(true_fraud: int, false_positive: int):
    return (
        [{"fraud_label": 1} for _ in range(true_fraud)]
        + [{"fraud_label": 0} for _ in range(false_positive)]
    )


def test_rejects_insufficient_training_data():
    service = FraudTrainingDataQualityService(
        minimum_samples=100
    )

    result = service.validate(
        make_cases(
            true_fraud=10,
            false_positive=10,
        )
    )

    assert result.is_valid is False
    assert result.total_samples == 20
    assert result.true_fraud_samples == 10
    assert result.false_positive_samples == 10
    assert "Insufficient" in result.reason


def test_rejects_dataset_without_true_fraud():
    service = FraudTrainingDataQualityService(
        minimum_samples=10
    )

    result = service.validate(
        make_cases(
            true_fraud=0,
            false_positive=20,
        )
    )

    assert result.is_valid is False
    assert result.true_fraud_samples == 0
    assert result.false_positive_samples == 20
    assert "TRUE_FRAUD" in result.reason


def test_rejects_dataset_without_false_positive():
    service = FraudTrainingDataQualityService(
        minimum_samples=10
    )

    result = service.validate(
        make_cases(
            true_fraud=20,
            false_positive=0,
        )
    )

    assert result.is_valid is False
    assert result.true_fraud_samples == 20
    assert result.false_positive_samples == 0
    assert "FALSE_POSITIVE" in result.reason


def test_accepts_valid_training_dataset():
    service = FraudTrainingDataQualityService(
        minimum_samples=10
    )

    result = service.validate(
        make_cases(
            true_fraud=30,
            false_positive=70,
        )
    )

    assert result.is_valid is True
    assert result.total_samples == 100
    assert result.true_fraud_samples == 30
    assert result.false_positive_samples == 70
    assert result.reason == "Training data is valid for model training"


def test_rejects_invalid_fraud_label():
    service = FraudTrainingDataQualityService(
        minimum_samples=2
    )

    with pytest.raises(
        ValueError,
        match="valid fraud label",
    ):
        service.validate(
            [
                {"fraud_label": 1},
                {"fraud_label": 2},
            ]
        )


def test_rejects_invalid_minimum_samples():
    with pytest.raises(ValueError):
        FraudTrainingDataQualityService(
            minimum_samples=1
        )