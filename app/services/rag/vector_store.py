from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    source: str
    content: str
    score: float


class VectorStore:
    """In-memory vector store using cosine similarity."""

    def __init__(self):
        self._items: list[dict] = []
        self._dimension: int | None = None

    def add(
        self,
        chunk_id: str,
        source: str,
        content: str,
        embedding: list[float],
    ) -> None:

        if not chunk_id.strip():
            raise ValueError("chunk_id cannot be empty")

        if not source.strip():
            raise ValueError("source cannot be empty")

        if not content.strip():
            raise ValueError("content cannot be empty")

        if not embedding:
            raise ValueError("embedding cannot be empty")
        if self._dimension is None:
            self._dimension = len(embedding)
        elif len(embedding) != self._dimension:
            raise ValueError(
        "embedding dimension does not match "
        "existing vectors"
    )

        self._items.append(
            {
                "chunk_id": chunk_id,
                "source": source,
                "content": content,
                "embedding": np.array(
                    embedding,
                    dtype=np.float32,
                ),
            }
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[SearchResult]:

        if not query_embedding:
            raise ValueError(
                "query_embedding cannot be empty"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0"
            )

        if not self._items:
            return []

        query = np.array(
            query_embedding,
            dtype=np.float32,
        )
        if (
    self._dimension is not None
    and len(query_embedding) != self._dimension
):
            raise ValueError(
        "query embedding dimension does not match "
        "stored vectors"
    )

        query_norm = np.linalg.norm(query)

        if query_norm == 0:
            raise ValueError(
                "query embedding cannot be zero"
            )

        results = []

        for item in self._items:
            vector = item["embedding"]

            vector_norm = np.linalg.norm(vector)

            if vector_norm == 0:
                continue

            score = float(
                np.dot(query, vector)
                / (query_norm * vector_norm)
            )

            results.append(
                SearchResult(
                    chunk_id=item["chunk_id"],
                    source=item["source"],
                    content=item["content"],
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]

    def count(self) -> int:
        return len(self._items)