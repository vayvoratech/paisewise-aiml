from uuid import UUID

from services import recommendation_cache


USER_ID = UUID("11111111-1111-1111-1111-111111111111")


def test_cache_recommendation(monkeypatch):
    stored = {}

    class MockRedisCache:
        def set(self, key, value, expiry=None):
            stored["key"] = key
            stored["value"] = value
            stored["expiry"] = expiry

    monkeypatch.setattr(
        recommendation_cache,
        "redis_cache",
        MockRedisCache()
    )

    recommendation = {
        "recommendationRunId": "test-run-id",
        "recommendedFunds": []
    }

    recommendation_cache.cache_recommendation(
        USER_ID,
        recommendation
    )

    assert stored["key"] == f"recommendation:{USER_ID}"
    assert stored["value"] == recommendation
    assert stored["expiry"] == 4 * 60 * 60


def test_invalidate_recommendation_cache(monkeypatch):
    deleted = {}

    class MockRedisCache:
        def delete(self, key):
            deleted["key"] = key

    monkeypatch.setattr(
        recommendation_cache,
        "redis_cache",
        MockRedisCache()
    )

    recommendation_cache.invalidate_recommendation_cache(USER_ID)

    assert deleted["key"] == f"recommendation:{USER_ID}"


def test_get_cached_recommendation(monkeypatch):
    recommendation = {
        "recommendationRunId": "test-run-id",
        "recommendedFunds": []
    }

    class MockRedisCache:
        def get(self, key):
            assert key == f"recommendation:{USER_ID}"
            return recommendation

    monkeypatch.setattr(
        recommendation_cache,
        "redis_cache",
        MockRedisCache()
    )

    result = recommendation_cache.get_cached_recommendation(
        USER_ID
    )

    assert result == recommendation