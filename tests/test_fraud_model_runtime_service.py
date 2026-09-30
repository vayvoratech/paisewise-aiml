import pytest

from app.services.fraud_model_runtime_service import (
    FraudModelRuntimeService,
)


class FakeFraudModel:
    def __init__(self, probability=0.85):
        self.probability = probability
        self.calls = 0

    def predict_proba(self, rows):
        self.calls += 1

        assert len(rows) == 1

        return [
            [
                1.0 - self.probability,
                self.probability,
            ]
        ]


class InvalidShapeModel:

    def predict_proba(self, rows):
        return [[0.1, 0.2, 0.7]]


class InvalidProbabilityModel:

    def predict_proba(self, rows):
        return [[0.2, 1.5]]


def test_model_is_kept_in_memory():
    model = FakeFraudModel()

    runtime = FraudModelRuntimeService(model)

    assert runtime.model is model


def test_predicts_using_in_memory_model():
    model = FakeFraudModel(probability=0.85)

    runtime = FraudModelRuntimeService(model)

    probability = runtime.predict_proba(
        [10.0, 2500.0, 25000.0, 1.0, 0.0, 1.0, 0.0]
    )

    assert probability == 0.85
    assert model.calls == 1


def test_multiple_predictions_reuse_same_model():
    model = FakeFraudModel(probability=0.75)

    runtime = FraudModelRuntimeService(model)

    first = runtime.predict_proba([1.0])
    second = runtime.predict_proba([2.0])

    assert first == 0.75
    assert second == 0.75
    assert runtime.model is model
    assert model.calls == 2


def test_rejects_missing_model():
    with pytest.raises(
        ValueError,
        match="fraud model is required",
    ):
        FraudModelRuntimeService(None)


def test_rejects_model_without_predict_proba():
    class InvalidModel:
        pass

    with pytest.raises(
        ValueError,
        match="predict_proba",
    ):
        FraudModelRuntimeService(
            InvalidModel()
        )


def test_rejects_empty_features():
    runtime = FraudModelRuntimeService(
        FakeFraudModel()
    )

    with pytest.raises(
        ValueError,
        match="features are required",
    ):
        runtime.predict_proba([])


def test_rejects_invalid_prediction_shape():
    runtime = FraudModelRuntimeService(
        InvalidShapeModel()
    )

    with pytest.raises(
        ValueError,
        match="exactly two class probabilities",
    ):
        runtime.predict_proba([1.0])


def test_rejects_invalid_probability():
    runtime = FraudModelRuntimeService(
        InvalidProbabilityModel()
    )

    with pytest.raises(
        ValueError,
        match="between 0 and 1",
    ):
        runtime.predict_proba([1.0])