import pytest

from app.services.fraud_model_training_service import (
    FraudModelTrainingService,
)
from app.services.fraud_training_data_quality_service import (
    FraudTrainingDataQualityService,
)


def build_dataset():
    cases = []

    for i in range(50):
        cases.append(
            {
                "features": [
                    1.0 + (i * 0.01),
                    100.0,
                    100.0 + i,
                    1.0,
                    0.0,
                    1.0,
                    0.0,
                ],
                "fraud_label": 0,
                "reviewer_decision": "FALSE_POSITIVE",
            }
        )

    for i in range(50):
        cases.append(
            {
                "features": [
                    20.0 + (i * 0.01),
                    10000.0,
                    200000.0 + i,
                    0.0,
                    1.0,
                    1.0,
                    0.0,
                ],
                "fraud_label": 1,
                "reviewer_decision": "TRUE_FRAUD",
            }
        )

    return cases

def test_rejects_invalid_label():
    quality_service = FraudTrainingDataQualityService(
        minimum_samples=2
    )

    service = FraudModelTrainingService(
        quality_service=quality_service
    )

    cases = [
        {
            "features": [1, 2, 3, 1, 0, 1, 0],
            "reviewer_decision": "TRUE_FRAUD",
            "fraud_label": 2,
        },
        {
            "features": [1, 2, 3, 0, 1, 1, 0],
            "reviewer_decision": "FALSE_POSITIVE",
            "fraud_label": 0,
        },
    ]

    with pytest.raises(
        ValueError,
        match="valid fraud label",
    ):
        service.train(cases)


def test_trains_model_and_returns_metrics():
    quality_service = FraudTrainingDataQualityService(
        minimum_samples=100
    )

    service = FraudModelTrainingService(
        quality_service=quality_service
    )

    result = service.train(build_dataset())

    assert result.model is not None
    assert result.training_samples > 0
    assert result.validation_samples > 0

    assert set(result.metrics) == {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
    }

    for metric in result.metrics.values():
        assert 0.0 <= metric <= 1.0

    assert hasattr(result.model, "predict_proba")


def test_training_is_blocked_when_data_is_insufficient():
    quality_service = FraudTrainingDataQualityService(
        minimum_samples=100
    )

    service = FraudModelTrainingService(
        quality_service=quality_service
    )

    cases = build_dataset()[:20]

    with pytest.raises(
        ValueError,
        match="Fraud model training blocked",
    ):
        service.train(cases)


def test_rejects_missing_features():
    quality_service = FraudTrainingDataQualityService(
        minimum_samples=2
    )

    service = FraudModelTrainingService(
        quality_service=quality_service
    )

    cases = [
        {
            "reviewer_decision": "TRUE_FRAUD",
            "fraud_label": 1,
        },
        {
            "reviewer_decision": "FALSE_POSITIVE",
            "fraud_label": 0,
        },
    ]

    with pytest.raises(ValueError, match="missing features"):
        service.train(cases)





def test_rejects_invalid_validation_size():
    quality_service = FraudTrainingDataQualityService(
        minimum_samples=2
    )

    with pytest.raises(ValueError):
        FraudModelTrainingService(
            quality_service=quality_service,
            validation_size=1.0,
        )