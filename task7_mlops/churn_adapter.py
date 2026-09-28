from app.services.churn_service import ChurnRequest, ChurnService


class ChurnScoreAdapter:
    """
    MLOps adapter for the existing Churn Score component.

    The original churn_service.py is not modified.
    """

    model_name = "Churn Score"
    model_version = "v1"
    model_type = "rule_based"

    def __init__(self) -> None:
        self.service = ChurnService()

    def predict(self, request: ChurnRequest):
        return self.service.calculate(request)

    def metadata(self) -> dict[str, str]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_type": self.model_type,
        }