import hashlib
from cache.redis_cache import RedisCache

cache = RedisCache()
CACHE_TTL = 12 * 60 * 60


def assign_lesson_variant(user_id: str) -> str:
    bucket = int(hashlib.sha256(str(user_id).encode()).hexdigest(), 16) % 100
    return "personalized" if bucket < 50 else "default"


def cache_lesson_recommendations(user_id: str, recommendations):
    cache.set(f"lesson_recommendations:{user_id}", recommendations, expiry=CACHE_TTL)


def get_cached_lesson_recommendations(user_id: str):
    return cache.get(f"lesson_recommendations:{user_id}")
