from app.services.fraud_model_runtime_service import (
    FraudModelRuntimeService,
)


class FraudRuntime:
    """
    Holds the already-loaded fraud model runtime.

    This is intentionally isolated from existing services and routes.
    """

    def __init__(self):
        self._runtime = None

    def initialize(self, model) -> None:
        if self._runtime is not None:
            raise RuntimeError(
                "Fraud model runtime is already initialized"
            )

        self._runtime = FraudModelRuntimeService(model)

    def get_runtime(self) -> FraudModelRuntimeService:
        if self._runtime is None:
            raise RuntimeError(
                "Fraud model runtime has not been initialized"
            )

        return self._runtime


fraud_runtime = FraudRuntime()