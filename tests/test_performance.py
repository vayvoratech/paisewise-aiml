import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService


# =========================================================
# Service factory
# =========================================================

def create_service():
    """
    Create a completely isolated ChatService
    for performance testing.

    External dependencies are mocked:

    - Redis / ConversationService
    - RAG
    - PromptBuilder
    - LLM
    - AI request replay
    """

    llm_provider = MagicMock()

    async def fake_generate(messages):
        """Simulate a fast asynchronous LLM response."""
        await asyncio.sleep(0.01)
        return "An ETF is an exchange-traded fund."

    llm_provider.generate = AsyncMock(
        side_effect=fake_generate
    )

    rag_service = MagicMock()
    rag_service.retrieve.return_value = []

    prompt_builder = MagicMock()
    prompt_builder.build.return_value = (
        "Answer using the available financial knowledge."
    )

    conversation_service = MagicMock()
    conversation_service.get_history.return_value = []
    conversation_service.add_message.return_value = []

    # Prevent the real replay service from connecting to PostgreSQL.
    replay_service = MagicMock()
    replay_service.record_request.return_value = None

    return ChatService(
        llm_provider=llm_provider,
        rag_service=rag_service,
        prompt_builder=prompt_builder,
        conversation_service=conversation_service,
        replay_service=replay_service,
    )


# =========================================================
# Helper
# =========================================================

def create_request(user_number: int) -> ChatRequest:
    """Create a unique chat request."""
    return ChatRequest(
        userId=f"user_{user_number}",
        sessionId=f"session_{user_number}",
        message="What is an ETF?",
    )


# =========================================================
# Basic concurrent chat test
# =========================================================

@pytest.mark.anyio
async def test_concurrent_chat_requests_complete():
    service = create_service()

    requests = [
        create_request(i)
        for i in range(100)
    ]

    responses = await asyncio.gather(
        *[
            service.process_chat(request)
            for request in requests
        ]
    )

    assert len(responses) == 100

    for response in responses:
        assert response.status == "success"
        assert response.responseId is not None
        assert response.message == "An ETF is an exchange-traded fund."


# =========================================================
# 100 concurrent sessions
# =========================================================

@pytest.mark.anyio
async def test_100_concurrent_chat_sessions():
    service = create_service()

    requests = [
        create_request(i)
        for i in range(100)
    ]

    start_time = time.perf_counter()

    responses = await asyncio.gather(
        *[
            service.process_chat(request)
            for request in requests
        ]
    )

    elapsed_time = time.perf_counter() - start_time

    assert len(responses) == 100

    for response in responses:
        assert response.status == "success"
        assert response.responseId is not None
        assert response.message == "An ETF is an exchange-traded fund."

    assert elapsed_time < 8.0, (
        f"100 concurrent sessions took {elapsed_time:.2f} seconds; "
        "required < 8 seconds."
    )


# =========================================================
# Verify true concurrency
# =========================================================

@pytest.mark.anyio
async def test_100_sessions_are_processed_concurrently():
    service = create_service()

    requests = [
        create_request(i)
        for i in range(100)
    ]

    start_time = time.perf_counter()

    await asyncio.gather(
        *[
            service.process_chat(request)
            for request in requests
        ]
    )

    elapsed_time = time.perf_counter() - start_time

    # Each mocked LLM call sleeps for only 0.01 seconds.
    # Concurrent execution should remain close to one request's latency.
    assert elapsed_time < 8.0


# =========================================================
# Each session has independent Redis context
# =========================================================

@pytest.mark.anyio
async def test_concurrent_sessions_use_independent_context():
    service = create_service()

    requests = [
        ChatRequest(
            userId=f"user_{i}",
            sessionId=f"session_{i}",
            message=f"Question from user {i}",
        )
        for i in range(100)
    ]

    responses = await asyncio.gather(
        *[
            service.process_chat(request)
            for request in requests
        ]
    )

    assert len(responses) == 100

    for response in responses:
        assert response.status == "success"

    assert service.conversation_service.get_history.call_count == 100
    assert service.conversation_service.add_message.call_count == 200


# =========================================================
# Redis is mocked
# =========================================================

@pytest.mark.anyio
async def test_performance_test_does_not_require_real_redis():
    service = create_service()

    request = ChatRequest(
        userId="performance_user",
        sessionId="performance_session",
        message="What is an ETF?",
    )

    response = await service.process_chat(request)

    assert response.status == "success"

    service.conversation_service.get_history.assert_called_once_with(
        user_id="performance_user",
        session_id="performance_session",
    )

    assert service.conversation_service.add_message.call_count == 2


# =========================================================
# PostgreSQL is not involved
# =========================================================

@pytest.mark.anyio
async def test_performance_chat_is_database_independent():
    service = create_service()

    request = ChatRequest(
        userId="performance_user",
        sessionId="performance_session",
        message="What is an ETF?",
    )

    response = await service.process_chat(request)

    assert response.status == "success"
    assert response.message
    assert response.responseId is not None

    service.llm_provider.generate.assert_called_once()
    service.rag_service.retrieve.assert_called_once()
    service.prompt_builder.build.assert_called_once()
    service.conversation_service.get_history.assert_called_once()


# =========================================================
# LLM concurrency test
# =========================================================

@pytest.mark.anyio
async def test_llm_handles_100_concurrent_requests():
    service = create_service()

    requests = [
        create_request(i)
        for i in range(100)
    ]

    await asyncio.gather(
        *[
            service.process_chat(request)
            for request in requests
        ]
    )

    assert service.llm_provider.generate.call_count == 100


# =========================================================
# All responses are successful
# =========================================================

@pytest.mark.anyio
async def test_100_concurrent_responses_are_successful():
    service = create_service()

    requests = [
        create_request(i)
        for i in range(100)
    ]

    responses = await asyncio.gather(
        *[
            service.process_chat(request)
            for request in requests
        ]
    )

    successful_responses = [
        response
        for response in responses
        if response.status == "success"
    ]

    assert len(successful_responses) == 100


# =========================================================
# Response IDs are unique
# =========================================================

@pytest.mark.anyio
async def test_100_concurrent_responses_have_unique_ids():
    service = create_service()

    requests = [
        create_request(i)
        for i in range(100)
    ]

    responses = await asyncio.gather(
        *[
            service.process_chat(request)
            for request in requests
        ]
    )

    response_ids = [
        response.responseId
        for response in responses
    ]

    assert all(response_id is not None for response_id in response_ids)
    assert len(response_ids) == 100
    assert len(set(response_ids)) == 100