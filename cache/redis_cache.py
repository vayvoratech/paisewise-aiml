import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()


class RedisCache:

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            host = os.getenv("REDIS_HOST")
            port = os.getenv("REDIS_PORT")

            if not host or not port:
                raise RuntimeError(
                    "REDIS_HOST and REDIS_PORT must be set to use the cache."
                )

            self._client = redis.Redis(
                host=host,
                port=int(port),
                password=os.getenv("REDIS_PASSWORD") or None,
                ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
                decode_responses=True,
            )

        return self._client

    def get(self, key):
        try:
            value = self._get_client().get(key)
        except Exception as error:
            print(f"Redis get() failed, treating as cache miss: {error}")
            return None

        if value:
            return json.loads(value)

        return None

    def set(self, key, value, expiry=None):
        try:
            value = json.dumps(value, default=str)
            self._get_client().set(key, value, ex=expiry)
        except Exception as error:
            print(f"Redis set() failed, continuing without caching: {error}")

    def delete(self, key):
        try:
            self._get_client().delete(key)
        except Exception as error:
            print(f"Redis delete() failed: {error}")