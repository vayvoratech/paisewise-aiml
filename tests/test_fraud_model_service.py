import pytest

from app.services.fraud_model_service import FraudModelService


class FakeFraudModel:
    def __init__(self, probabilities):
        self.probabilities = probabilities
        self.calls = 0

    def predict_proba(self, features):
        self.calls += 1
        return self.probabilities


def test_predict_fraud_probability():
    model = FakeFraudModel([[0.15, 0.85]])
    service = FraudModelService(model)

    probability = service.predict_fraud_probability(
        [10.0, 2500.0, 25000.0, 1.0, 0.0, 1.0, 0.0]
    )

    assert probability == 0.85
    assert model.calls == 1


def test_predict_low_fraud_probability():
    model = FakeFraudModel([[0.92, 0.08]])
    service = FraudModelService(model)

    probability = service.predict_fraud_probability([1.0] * 7)

    assert probability == 0.08


def test_model_cannot_be_none():
    with pytest.raises(ValueError, match="model cannot be None"):
        FraudModelService(None)


def test_model_requires_predict_proba():
    class InvalidModel:
        pass

    with pytest.raises(
        TypeError,
        match="model must provide a callable predict_proba method",
    ):
        FraudModelService(InvalidModel())


def test_empty_features_are_rejected():
    model = FakeFraudModel([[0.15, 0.85]])
    service = FraudModelService(model)

    with pytest.raises(
        ValueError,
        match="features cannot be empty",
    ):
        service.predict_fraud_probability([])


def test_multiple_predictions_are_rejected():
    model = FakeFraudModel(
        [
            [0.15, 0.85],
            [0.90, 0.10],
        ]
    )
    service = FraudModelService(model)

    with pytest.raises(
        ValueError,
        match="exactly one prediction",
    ):
        service.predict_fraud_probability([1.0] * 7)


def test_wrong_number_of_classes_is_rejected():
    model = FakeFraudModel([[1.0]])
    service = FraudModelService(model)

    with pytest.raises(
        ValueError,
        match="probabilities for two classes",
    ):
        service.predict_fraud_probability([1.0] * 7)


@pytest.mark.parametrize(
    "probabilities",
    [
        [[1.2, -0.2]],
        [[-0.1, 1.1]],
    ],
)
def test_invalid_probability_is_rejected(probabilities):
    model = FakeFraudModel(probabilities)
    service = FraudModelService(model)

    with pytest.raises(
        ValueError,
        match="fraud probability must be between 0 and 1",
    ):
        service.predict_fraud_probability([1.0] * 7)