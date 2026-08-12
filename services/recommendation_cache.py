from cache.redis_cache import RedisCache


redis_cache = RedisCache()

RECOMMENDATION_CACHE_TTL = 4 * 60 * 60


def get_recommendation_cache_key(user_id):
    return f"recommendation:{user_id}"


def get_cached_recommendation(user_id):
    key = get_recommendation_cache_key(user_id)
    return redis_cache.get(key)


def cache_recommendation(user_id, recommendations):
    key = get_recommendation_cache_key(user_id)

    redis_cache.set(
        key,
        recommendations,
        expiry=RECOMMENDATION_CACHE_TTL
    )


def invalidate_recommendation_cache(user_id):
    key = get_recommendation_cache_key(user_id)
    redis_cache.delete(key)