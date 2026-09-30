import hashlib
import json
from inspect import isawaitable
from typing import Any

from app.services.rag.vector_store import SearchResult


class RAGQueryCacheService:
    """Short-lived shared cache for retrieved knowledge chunks."""

    TTL_SECONDS = 600
    KEY_PREFIX = "rag:query:v1"
    TOP_K = 5

    def __init__(self, redis_client: Any) -> None:
        self.redis = redis_client

    @classmethod
    def _key(cls, query: str) -> str:
        normalized = " ".join(query.split())
        digest = hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

        return f"{cls.KEY_PREFIX}:{cls.TOP_K}:{digest}"

    async def get(self, query: str) -> list[SearchResult] | None:
        cached = await self.redis.get(self._key(query))

        if cached is None:
            return None

        try:
            rows = json.loads(cached)

            return [
                SearchResult(
                    chunk_id=row["chunk_id"],
                    source=row["source"],
                    content=row["content"],
                    score=float(row["score"]),
                )
                for row in rows
            ]
        except (TypeError, ValueError, KeyError):
            return None

    async def set(
        self,
        query: str,
        results: list[SearchResult],
    ) -> None:
        if not all(isinstance(row, SearchResult) for row in results):
            return

        payload = [
            {
                "chunk_id": row.chunk_id,
                "source": row.source,
                "content": row.content,
                "score": row.score,
            }
            for row in results
        ]

        await self.redis.set(
            self._key(query),
            json.dumps(payload),
            ex=self.TTL_SECONDS,
        )

    async def prewarm(
        self,
        rag_service: Any,
        queries: list[str],
    ) -> int:
        """Cache retrieved chunks for configured common questions."""
        warmed_count = 0

        for query in queries:
            query = query.strip()

            if not query:
                continue

            try:
                cached = await self.get(query)

                if cached is not None:
                    continue

                results = rag_service.retrieve(query)

                if isawaitable(results):
                    results = await results

                if not isinstance(results, list):
                    continue

                if not all(
                    isinstance(result, SearchResult)
                    for result in results
                ):
                    continue

                await self.set(query, results)
                warmed_count += 1

            except Exception:
                # Prewarming is optional; failures must not block startup.
                continue

        return warmed_count