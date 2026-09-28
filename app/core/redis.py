import os

import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3,
    health_check_interval=30,
)