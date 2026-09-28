from task7_mlops.model_adapters import ModelAdapterRegistry
from task7_mlops.topic_detection_adapter import TopicDetectionAdapter
from task7_mlops.churn_adapter import ChurnScoreAdapter
from task7_mlops.rag_embedding_adapter import RAGEmbeddingAdapter


class Task7ModelRegistry:
    """
    Central registry for the five Task 7 model/components.

    Existing application files are not modified.
    """

    def __init__(self) -> None:
        self.registry = ModelAdapterRegistry()

        self.topic_detection = TopicDetectionAdapter()
        self.churn_score = ChurnScoreAdapter()
        self.rag_embedding = RAGEmbeddingAdapter()

        self.registry.add(
            self._to_adapter(
                self.topic_detection
            )
        )

        self.registry.add(
            self._to_adapter(
                self.churn_score
            )
        )

        self.registry.add(
            self._to_adapter(
                self.rag_embedding
            )
        )

    @staticmethod
    def _to_adapter(component):
        from task7_mlops.model_adapters import ModelAdapter

        return ModelAdapter(
            name=component.model_name,
            version=component.model_version,
            predictor=component.predict,
            model_type=component.model_type,
        )

    def list_models(self) -> list[str]:
        return self.registry.list_models()

    def get_model(self, model_name: str):
        return self.registry.get(model_name)