import json
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.conversation_service import (
    ConversationService,
    MAX_MESSAGES,
    CHAT_TTL_SECONDS,
)


@pytest.fixture
def redis_mock():
    mock = AsyncMock()
    return mock


@pytest.fixture
def service(redis_mock):
    return ConversationService(redis_mock)


# =========================================================
# KEY CREATION
# =========================================================

def test_build_key():
    key = ConversationService.build_key(
        "user123",
        "session456",
    )

    assert key == "chat:user123:session456"


@pytest.mark.parametrize(
    "user_id",
    ["", "   "],
)
def test_invalid_user_id(user_id):
    with pytest.raises(ValueError):
        ConversationService.build_key(
            user_id,
            "session1",
        )


@pytest.mark.parametrize(
    "session_id",
    ["", "   "],
)
def test_invalid_session_id(session_id):
    with pytest.raises(ValueError):
        ConversationService.build_key(
            "user1",
            session_id,
        )


# =========================================================
# EMPTY HISTORY
# =========================================================

@pytest.mark.anyio
async def test_empty_history(service, redis_mock):

    redis_mock.get.return_value = None

    history = await service.get_history(
        "user1",
        "session1",
    )

    assert history == []

    redis_mock.get.assert_awaited_once_with(
        "chat:user1:session1"
    )


# =========================================================
# EXISTING HISTORY
# =========================================================

@pytest.mark.anyio
async def test_get_existing_history(service, redis_mock):

    stored_history = [
        {
            "role": "user",
            "content": "What is an ETF?",
        },
        {
            "role": "assistant",
            "content": "An ETF is an exchange-traded fund.",
        },
    ]

    redis_mock.get.return_value = json.dumps(
        stored_history
    )

    history = await service.get_history(
        "user1",
        "session1",
    )

    assert history == stored_history


# =========================================================
# REDIS BYTE RESPONSE
# =========================================================

@pytest.mark.anyio
async def test_get_history_from_bytes(
    service,
    redis_mock,
):

    history = [
        {
            "role": "user",
            "content": "Hello",
        }
    ]

    redis_mock.get.return_value = json.dumps(
        history
    ).encode("utf-8")

    result = await service.get_history(
        "user1",
        "session1",
    )

    assert result == history


# =========================================================
# ADD MESSAGE
# =========================================================

@pytest.mark.anyio
async def test_add_message(
    service,
    redis_mock,
):

    redis_mock.get.return_value = None

    history = await service.add_message(
        user_id="user1",
        session_id="session1",
        role="user",
        content="What is an ETF?",
    )

    assert history == [
        {
            "role": "user",
            "content": "What is an ETF?",
        }
    ]

    redis_mock.set.assert_awaited_once()

    args, kwargs = redis_mock.set.call_args

    assert args[0] == "chat:user1:session1"
    assert kwargs["ex"] == CHAT_TTL_SECONDS


# =========================================================
# TTL MUST BE 4 HOURS
# =========================================================

def test_chat_ttl_is_four_hours():

    assert CHAT_TTL_SECONDS == 14400


# =========================================================
# MAXIMUM CONTEXT = 10
# =========================================================

def test_max_messages_is_ten():

    assert MAX_MESSAGES == 10


# =========================================================
# TRIM HISTORY
# =========================================================

@pytest.mark.anyio
async def test_history_keeps_latest_ten(
    service,
    redis_mock,
):

    old_history = [
        {
            "role": "user",
            "content": f"message {i}",
        }
        for i in range(10)
    ]

    redis_mock.get.return_value = json.dumps(
        old_history
    )

    history = await service.add_message(
        user_id="user1",
        session_id="session1",
        role="assistant",
        content="message 10",
    )

    assert len(history) == 10

    # Oldest message removed
    assert history[0]["content"] == "message 1"

    # Newest message retained
    assert history[-1]["content"] == "message 10"


# =========================================================
# MESSAGE ORDER
# =========================================================

@pytest.mark.anyio
async def test_message_order_is_preserved(
    service,
    redis_mock,
):

    old_history = [
        {
            "role": "user",
            "content": "first",
        },
        {
            "role": "assistant",
            "content": "second",
        },
    ]

    redis_mock.get.return_value = json.dumps(
        old_history
    )

    history = await service.add_message(
        "user1",
        "session1",
        "user",
        "third",
    )

    assert history[0]["content"] == "first"
    assert history[1]["content"] == "second"
    assert history[2]["content"] == "third"


# =========================================================
# CLEAR HISTORY
# =========================================================

@pytest.mark.anyio
async def test_clear_history(
    service,
    redis_mock,
):

    await service.clear_history(
        "user1",
        "session1",
    )

    redis_mock.delete.assert_awaited_once_with(
        "chat:user1:session1"
    )


# =========================================================
# INVALID REDIS DATA
# =========================================================

@pytest.mark.anyio
async def test_invalid_json_in_redis(
    service,
    redis_mock,
):

    redis_mock.get.return_value = "not-valid-json"

    with pytest.raises(ValueError):
        await service.get_history(
            "user1",
            "session1",
        )


@pytest.mark.anyio
async def test_non_list_history(
    service,
    redis_mock,
):

    redis_mock.get.return_value = json.dumps(
        {"role": "user"}
    )

    with pytest.raises(ValueError):
        await service.get_history(
            "user1",
            "session1",
        )


# =========================================================
# INVALID MESSAGE INPUT
# =========================================================

@pytest.mark.anyio
async def test_invalid_role_type(service):

    with pytest.raises(TypeError):

        await service.add_message(
            "user1",
            "session1",
            123,
            "hello",
        )


@pytest.mark.anyio
async def test_invalid_content_type(service):

    with pytest.raises(TypeError):

        await service.add_message(
            "user1",
            "session1",
            "user",
            123,
        )


@pytest.mark.anyio
async def test_empty_role(service):

    with pytest.raises(ValueError):

        await service.add_message(
            "user1",
            "session1",
            "",
            "hello",
        )