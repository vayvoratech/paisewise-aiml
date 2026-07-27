import time
from cache.redis_cache import RedisCache


cache = RedisCache()


MAX_REQUESTS = 10
WINDOW_SECONDS = 60


def check_rate_limit(user_id):

    key = f"rate_limit:{user_id}"

    current_requests = cache.get(key)

    if current_requests is None:

        cache.set(
            key,
            1,
            expiry=WINDOW_SECONDS
        )

        return True


    if current_requests >= MAX_REQUESTS:

        return False


    cache.set(
        key,
        current_requests + 1,
        expiry=WINDOW_SECONDS
    )

    return True