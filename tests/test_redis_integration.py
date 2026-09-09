import redis

from app.services.conversation_service import (
    ConversationService,
    CHAT_TTL_SECONDS,
    MAX_MESSAGES,
)


def test_real_redis_conversation():

    client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
    )

    assert client.ping() is True

    service = ConversationService(client)

    user_id = "test_user"
    session_id = "test_session"

    # Start clean.
    service.clear_history(
        user_id,
        session_id,
    )

    # Add first message.
    history = service.add_message(
        user_id=user_id,
        session_id=session_id,
        role="user",
        content="What is an ETF?",
    )

    assert len(history) == 1
    assert history[0]["role"] == "user"

    # Add second message.
    history = service.add_message(
        user_id=user_id,
        session_id=session_id,
        role="assistant",
        content="An ETF is an exchange-traded fund.",
    )

    assert len(history) == 2

    # Verify retrieval.
    stored = service.get_history(
        user_id,
        session_id,
    )

    assert stored == history

    # Verify TTL.
    key = service.build_key(
        user_id,
        session_id,
    )

    ttl = client.ttl(key)

    assert 0 < ttl <= CHAT_TTL_SECONDS

    # Verify maximum 10 messages.
    for i in range(3, 15):
        service.add_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=f"message {i}",
        )

    history = service.get_history(
        user_id,
        session_id,
    )

    assert len(history) == MAX_MESSAGES

    # Cleanup.
    service.clear_history(
        user_id,
        session_id,
    )

    assert service.get_history(
        user_id,
        session_id,
    ) == []