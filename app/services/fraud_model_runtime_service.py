from typing import Any


class FraudModelRuntimeService:
    """
    Holds the fraud model in memory for runtime inference.

    The model is loaded before this service is created.
    No filesystem access is performed during inference.
    """

    def __init__(self, model: Any):
        if model is None:
            raise ValueError("fraud model is required")

        predict_proba = getattr(model, "predict_proba", None)

        if not callable(predict_proba):
            raise ValueError(
                "fraud model must provide a callable predict_proba method"
            )

        self._model = model

    @property
    def model(self) -> Any:
        return self._model

    def predict_proba(self, features: list[float]) -> float:
        if not features:
            raise ValueError("features are required")

        probabilities = self._model.predict_proba(
            [features]
        )

        if len(probabilities) != 1:
            raise ValueError(
                "fraud model must return exactly one prediction"
            )

        prediction = probabilities[0]

        if len(prediction) != 2:
            raise ValueError(
                "fraud model must return exactly two class probabilities"
            )

        fraud_probability = float(prediction[1])

        if not 0.0 <= fraud_probability <= 1.0:
            raise ValueError(
                "fraud probability must be between 0 and 1"
            )

        return fraud_probability