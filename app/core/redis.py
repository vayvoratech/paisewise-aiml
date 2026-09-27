import os

import redis
from dotenv import load_dotenv


load_dotenv()


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    password=os.getenv("REDIS_PASSWORD") or None,
    ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
    decode_responses=True,
)
