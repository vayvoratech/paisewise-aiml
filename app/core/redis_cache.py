from app.core.redis import redis_client


class RedisCache:
    def __init__(self):
        self.client = redis_client

    def get(self, key):
        if self.client is None:
            return None

        try:
            return self.client.get(key)
        except Exception:
            return None

    def set(self, key, value, ttl=None, expiry=None):
        if self.client is None:
            return False

        seconds = expiry if expiry is not None else ttl

        try:
            if seconds:
                return self.client.setex(key, seconds, value)

            return self.client.set(key, value)
        except Exception:
            return False

    def delete(self, key):
        if self.client is None:
            return False

        try:
            return self.client.delete(key)
        except Exception:
            return False
