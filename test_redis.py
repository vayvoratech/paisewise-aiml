# import asyncio

# from app.core.redis import redis_client


# async def main():
#     print("PING:", await redis_client.ping())

#     key = (
#         "chat:"
#         "f6929d8f-8216-4f1b-8f10-4b2497db496a:"
#         "ttft-test-session:"
#         "profile"
#     )

#     start = asyncio.get_running_loop().time()

#     value = await redis_client.get(key)

#     elapsed = (
#         asyncio.get_running_loop().time()
#         - start
#     ) * 1000

#     print("PROFILE:", value)
#     print(f"PROFILE GET TIME: {elapsed:.2f} ms")

#     await redis_client.aclose()


# asyncio.run(main())


import asyncio

import pytest
from redis.exceptions import ConnectionError

from app.core.redis import redis_client


@pytest.mark.asyncio
async def test_redis_connection():
    try:
        print("PING:", await redis_client.ping())

        key = (
            "chat:"
            "f6929d8f-8216-4f1b-8f10-4b2497db496a:"
            "ttft-test-session:"
            "profile"
        )

        start = asyncio.get_running_loop().time()

        value = await redis_client.get(key)

        elapsed = (
            asyncio.get_running_loop().time()
            - start
        ) * 1000

        print("PROFILE:", value)
        print(
            f"PROFILE GET TIME: {elapsed:.2f} ms"
        )

    except ConnectionError:
        pytest.skip(
            "Redis is not running at "
            "127.0.0.1:6379"
        )

    finally:
        await redis_client.aclose()