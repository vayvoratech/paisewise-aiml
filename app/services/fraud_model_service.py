from typing import Any, Sequence


class FraudModelService:
    def __init__(self, model: Any):
        if model is None:
            raise ValueError("model cannot be None")

        predict_proba = getattr(model, "predict_proba", None)

        if not callable(predict_proba):
            raise TypeError(
                "model must provide a callable predict_proba method"
            )

        self._model = model

    def predict_fraud_probability(
        self,
        features: Sequence[float],
    ) -> float:
        if not features:
            raise ValueError("features cannot be empty")

        probabilities = self._model.predict_proba([list(features)])

        if len(probabilities) != 1:
            raise ValueError(
                "model must return exactly one prediction"
            )

        prediction = probabilities[0]

        if len(prediction) != 2:
            raise ValueError(
                "model must return probabilities for two classes"
            )

        fraud_probability = float(prediction[1])

        if not 0.0 <= fraud_probability <= 1.0:
            raise ValueError(
                "fraud probability must be between 0 and 1"
            )

        return fraud_probability