from app.services.rag.embedding_service import EmbeddingService


class RAGEmbeddingAdapter:
    """
    MLOps adapter for the existing RAG Embedding model.

    The original embedding_service.py is not modified.
    """

    model_name = "RAG Embedding"
    model_version = "v1"
    model_type = "sentence_transformer"

    def __init__(
        self,
        embedding_model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.service = EmbeddingService(
            model_name=embedding_model_name,
        )

    def predict(self, text: str) -> list[float]:
        return self.service.embed_text(text)

    def predict_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return self.service.embed_documents(texts)

    def metadata(self) -> dict[str, str]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_type": self.model_type,
            "embedding_model": self.service.model_name,
        }