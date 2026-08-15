import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()
class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            decode_responses=True
        )
    def get(self, key):
        value = self.client.get(key)

        if value:
            return json.loads(value)

        return None
    def set(self, key, value, expiry=None):
        value = json.dumps(value, default=str)

        self.client.set(
            key,
            value,
            ex=expiry
        )
    def delete(self, key):
        self.client.delete(key) 