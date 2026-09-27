from dataclasses import replace

from app.services.rag.vector_store import SearchResult


class Reranker:
    """Simple lexical reranker used after vector retrieval."""

    def rerank(self, query: str, results: list[SearchResult], top_k: int = 5) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("query cannot be empty")

        terms = {word.lower() for word in query.split() if len(word) > 2}
        scored = []
        for result in results:
            words = {word.lower().strip(".,!?():;") for word in result.content.split()}
            overlap = len(terms & words) / max(len(terms), 1)
            score = (result.score * 0.7) + (overlap * 0.3)
            scored.append(replace(result, score=score))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]
