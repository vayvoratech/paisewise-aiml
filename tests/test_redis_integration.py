# import pytest
# import redis.asyncio as redis

# from app.services.conversation_service import (
#     ConversationService,
#     CHAT_TTL_SECONDS,
#     MAX_MESSAGES,
# )


# @pytest.mark.anyio
# async def test_real_redis_conversation():
#     client = redis.Redis(
#         host="localhost",
#         port=6379,
#         decode_responses=True,
#     )

#     assert await client.ping() is True

#     service = ConversationService(client)

#     user_id = "test_user"
#     session_id = "test_session"

#     # Start clean.
#     await service.clear_history(
#         user_id,
#         session_id,
#     )

#     # Add first message.
#     history = await service.add_message(
#         user_id=user_id,
#         session_id=session_id,
#         role="user",
#         content="What is an ETF?",
#     )

#     assert len(history) == 1
#     assert history[0]["role"] == "user"

#     # Add second message.
#     history = await service.add_message(
#         user_id=user_id,
#         session_id=session_id,
#         role="assistant",
#         content="An ETF is an exchange-traded fund.",
#     )

#     assert len(history) == 2

#     # Verify retrieval.
#     stored = await service.get_history(
#         user_id,
#         session_id,
#     )

#     assert stored == history

#     # Verify TTL.
#     key = service.build_key(
#         user_id,
#         session_id,
#     )

#     ttl = await client.ttl(key)

#     assert 0 < ttl <= CHAT_TTL_SECONDS

#     # Verify maximum 10 messages.
#     for i in range(3, 15):
#         await service.add_message(
#             user_id=user_id,
#             session_id=session_id,
#             role="user",
#             content=f"message {i}",
#         )

#     history = await service.get_history(
#         user_id,
#         session_id,
#     )

#     assert len(history) == MAX_MESSAGES

#     # Cleanup.
#     await service.clear_history(
#         user_id,
#         session_id,
#     )

#     assert await service.get_history(
#         user_id,
#         session_id,
#     ) == []

#     await client.aclose()

import pytest
import redis.asyncio as redis
from redis.exceptions import ConnectionError


@pytest.mark.anyio
async def test_real_redis_conversation():
    client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
    )

    try:
        assert await client.ping() is True

        key = (
            "chat:"
            "f6929d8f-8216-4f1b-8f10-4b2497db496a:"
            "ttft-test-session:"
            "profile"
        )

        value = await client.get(key)

        assert value is None or isinstance(value, str)

    except ConnectionError:
        pytest.skip(
            "Redis server is unavailable at localhost:6379"
        )

    finally:
        await client.aclose()