from dataclasses import dataclass
from typing import Any

from app.services.rag.embedding_service import EmbeddingService


@dataclass
class RAGShadowResult:
    input_text: str
    current_embedding: list[float]
    shadow_embedding: list[float]
    similarity: float
    anomaly: bool


class RAGShadowDeployment:
    """
    Runs the current and shadow RAG embedding models on the same input.

    Existing application files are not modified.
    """

    def __init__(
        self,
        current_model_name: str = "all-MiniLM-L6-v2",
        shadow_model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.95,
    ) -> None:

        if not 0 < similarity_threshold <= 1:
            raise ValueError(
                "similarity_threshold must be between 0 and 1"
            )

        self.current_service = EmbeddingService(
            model_name=current_model_name
        )

        self.shadow_service = EmbeddingService(
            model_name=shadow_model_name
        )

        self.similarity_threshold = similarity_threshold

    @staticmethod
    def cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:

        if not vector_a or not vector_b:
            raise ValueError("embedding vectors cannot be empty")

        if len(vector_a) != len(vector_b):
            raise ValueError(
                "embedding vectors must have the same dimension"
            )

        dot_product = sum(
            a * b
            for a, b in zip(vector_a, vector_b)
        )

        magnitude_a = sum(
            a * a
            for a in vector_a
        ) ** 0.5

        magnitude_b = sum(
            b * b
            for b in vector_b
        ) ** 0.5

        if magnitude_a == 0 or magnitude_b == 0:
            raise ValueError(
                "embedding vector magnitude cannot be zero"
            )

        return dot_product / (
            magnitude_a * magnitude_b
        )

    def compare(
        self,
        input_text: str,
    ) -> RAGShadowResult:

        current_embedding = (
            self.current_service.embed_text(input_text)
        )

        shadow_embedding = (
            self.shadow_service.embed_text(input_text)
        )

        similarity = self.cosine_similarity(
            current_embedding,
            shadow_embedding,
        )

        anomaly = (
            similarity < self.similarity_threshold
        )

        return RAGShadowResult(
            input_text=input_text,
            current_embedding=current_embedding,
            shadow_embedding=shadow_embedding,
            similarity=similarity,
            anomaly=anomaly,
        )