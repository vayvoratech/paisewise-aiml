import os

import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
<<<<<<< HEAD
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    password=os.getenv("REDIS_PASSWORD") or None,
    ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
    decode_responses=True,
)
=======
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3,
    health_check_interval=30,
)
>>>>>>> srikanth_paise_wise_aiml
