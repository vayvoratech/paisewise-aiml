from __future__ import annotations

import hashlib
import inspect
import json
from typing import Any
from uuid import uuid4


class RAGQueryPopularityService:
    """Tracks recent query popularity in shared Redis."""

    ZSET_KEY = "rag:query-popularity:v1"
    QUERY_HASH_KEY = "rag:query-text:v1"

    WINDOW_SECONDS = 7 * 24 * 60 * 60
    MAX_TRACKED_QUERIES = 500

    def __init__(self, redis_client: Any) -> None:
        self.redis = redis_client

    @staticmethod
    def _normalize(query: str) -> str:
        return " ".join(query.split())

    @staticmethod
    def _digest(query: str) -> str:
        return hashlib.sha256(
            query.encode("utf-8")
        ).hexdigest()

    async def record(self, query: str) -> None:
        normalized = self._normalize(query)

        if not normalized or len(normalized) > 1000:
            return

        digest = self._digest(normalized)

        # A pipeline reduces round trips to Redis.
        async with self.redis.pipeline(transaction=False) as pipeline:
            pipeline.zincrby(self.ZSET_KEY, 1, digest)
            pipeline.hset(self.QUERY_HASH_KEY, digest, normalized)
            pipeline.expire(self.ZSET_KEY, self.WINDOW_SECONDS)
            pipeline.expire(self.QUERY_HASH_KEY, self.WINDOW_SECONDS)
            await pipeline.execute()

        # Keep the popularity index bounded.
        count = await self.redis.zcard(self.ZSET_KEY)
        if count > self.MAX_TRACKED_QUERIES:
            remove_count = count - self.MAX_TRACKED_QUERIES
            old_rows = await self.redis.zrange(
                self.ZSET_KEY,
                0,
                remove_count - 1,
            )

            if old_rows:
                async with self.redis.pipeline(transaction=False) as pipeline:
                    pipeline.zrem(self.ZSET_KEY, *old_rows)
                    pipeline.hdel(self.QUERY_HASH_KEY, *old_rows)
                    await pipeline.execute()

    async def get_popular_queries(
        self,
        *,
        limit: int = 10,
        minimum_uses: int = 3,
    ) -> list[str]:
        rows = await self.redis.zrevrange(
            self.ZSET_KEY,
            0,
            max(0, limit - 1),
            withscores=True,
        )

        popular: list[str] = []

        for digest, score in rows:
            if float(score) < minimum_uses:
                continue

            query = await self.redis.hget(
                self.QUERY_HASH_KEY,
                digest,
            )

            if query:
                popular.append(query)

        return popular


class PredictiveRAGCacheService:
    """
    Wraps the existing RAG query cache.

    ChatService can keep using the same get(query) and set(query, results)
    interface. Queries are counted when the wrapper's get() is called.
    """

    PREWARM_LOCK_KEY = "rag:query-prewarm-lock:v1"

    def __init__(
        self,
        cache_service: Any,
        popularity_service: RAGQueryPopularityService,
    ) -> None:
        self.cache_service = cache_service
        self.popularity_service = popularity_service

    async def get(self, query: str) -> Any:
        # Popularity tracking is best-effort and must not break chat.
        try:
            await self.popularity_service.record(query)
        except Exception:
            pass

        return await self.cache_service.get(query)

    async def set(self, query: str, results: Any) -> Any:
        return await self.cache_service.set(query, results)

    async def prewarm(
        self,
        *,
        rag_service: Any,
        queries: list[str] | None = None,
        limit: int = 10,
        minimum_uses: int = 3,
    ) -> int:
        """
        Warm popular queries, or an explicit query list if one is supplied.

        A Redis lock prevents every API instance from warming the same
        queries simultaneously during multi-instance startup.
        """
        if queries is None:
            queries = await self.popularity_service.get_popular_queries(
                limit=limit,
                minimum_uses=minimum_uses,
            )

        normalized_queries = [
            " ".join(query.split())
            for query in queries
            if query and query.strip()
        ]

        if not normalized_queries:
            return 0

        token = str(uuid4())
        acquired = await self.cache_service.redis.set(
            self.PREWARM_LOCK_KEY,
            token,
            nx=True,
            ex=120,
        )

        if not acquired:
            return 0

        warmed = 0

        try:
            retrieve = getattr(rag_service, "retrieve", None)
            if retrieve is None:
                return 0

            for query in normalized_queries:
                try:
                    cached = await self.cache_service.get(query)
                    if cached is not None:
                        continue

                    try:
                        results = retrieve(query)
                    except TypeError:
                        results = retrieve(query=query)

                    if inspect.isawaitable(results):
                        results = await results

                    await self.cache_service.set(query, results)
                    warmed += 1

                except Exception:
                    # One failed retrieval should not block other queries.
                    continue

            return warmed

        finally:
            # Delete the lock only if this instance still owns it.
            await self.cache_service.redis.eval(
                """
                if redis.call('get', KEYS[1]) == ARGV[1] then
                    return redis.call('del', KEYS[1])
                end
                return 0
                """,
                1,
                self.PREWARM_LOCK_KEY,
                token,
            )