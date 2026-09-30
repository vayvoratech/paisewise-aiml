from app.services.topic_classifier import classify_question


class TopicDetectionAdapter:
    """
    MLOps adapter for the existing Topic Detection component.

    The existing application code is not modified.
    This adapter only provides a standard predict interface.
    """

    model_name = "Topic Detection"
    model_version = "v1"
    model_type = "rule_based"

    def predict(self, question: str):
        return classify_question(question)

    def metadata(self) -> dict[str, str]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_type": self.model_type,
        }