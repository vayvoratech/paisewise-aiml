import json
from typing import Any

from app.core.redis import redis_client


class NewsCacheService:
    TTL_SECONDS = 2 * 60 * 60
    KEY_PREFIX = "news"

    @classmethod
    def _key(cls, cache_key: str) -> str:
        return f"{cls.KEY_PREFIX}:{cache_key}"

    @classmethod
    def get(cls, cache_key: str) -> Any | None:
        value = redis_client.get(cls._key(cache_key))

        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    @classmethod
    def set(cls, cache_key: str, value: Any) -> None:
        redis_client.setex(
            cls._key(cache_key),
            cls.TTL_SECONDS,
            json.dumps(value),
        )

    @classmethod
    def delete(cls, cache_key: str) -> None:
        redis_client.delete(cls._key(cache_key))

    @classmethod
    def get_news_cache(cls, cache_key: str) -> dict[str, Any] | None:
        """
        Return a cached news result together with its freshness metadata.

        Expected structure:

        {
            "articles": [...],
            "latest_article_key": "...",
            "latest_published_at": "..."
        }
        """
        cached = cls.get(cache_key)

        if not isinstance(cached, dict):
            return None

        if "articles" not in cached:
            return None

        return cached

    @classmethod
    def set_news_cache(
        cls,
        cache_key: str,
        articles: list[dict[str, Any]],
        latest_article_key: str | None,
        latest_published_at: str | None,
    ) -> None:
        """
        Cache processed news together with enough source metadata
        to determine whether newer articles are available.

        The entire entry still expires after 2 hours.
        """
        payload = {
            "articles": articles,
            "latest_article_key": latest_article_key,
            "latest_published_at": latest_published_at,
        }

        cls.set(cache_key, payload)

    @classmethod
    def is_newer_article_available(
        cls,
        cached: dict[str, Any],
        latest_article_key: str | None,
        latest_published_at: str | None,
    ) -> bool:
        """
        Return True only when the source contains a newer/different
        latest article than the one used to create the cached result.
        """

        if not cached:
            return True

        cached_key = cached.get("latest_article_key")
        cached_published_at = cached.get("latest_published_at")

        # A different article identity means new source content.
        if latest_article_key and cached_key:
            return latest_article_key != cached_key

        # If article identity is unavailable, compare timestamps.
        if latest_published_at and cached_published_at:
            return latest_published_at != cached_published_at

        # No freshness metadata means the cache cannot be trusted
        # for the refresh-only-when-new requirement.
        return True