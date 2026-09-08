import time
from cache.redis_cache import RedisCache

cache = RedisCache()
MAX_REQUESTS = 10
WINDOW_SECONDS = 60


def check_rate_limit(user_id):
    key = f"rate_limit:{user_id}"
    current = cache.get(key)
    if current is None:
        cache.set(key, 1, expiry=WINDOW_SECONDS)
        return True
    if int(current) >= MAX_REQUESTS:
        return False
    cache.set(key, int(current) + 1, expiry=WINDOW_SECONDS)
    return True
