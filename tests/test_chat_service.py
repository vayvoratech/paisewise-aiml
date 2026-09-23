import pytest
from unittest.mock import AsyncMock, MagicMock

from app.schemas.chat import (
    ChatRequest,
    UserContext,
)
from app.services.chat_service import ChatService


# =========================================================
# Mock Conversation Service
# =========================================================

def create_conversation_service(history=None):
    """
    Create a mocked ConversationService.

    Redis is mocked so these tests do not require
    a real Redis server.
    """

    conversation_service = MagicMock()

    conversation_service.get_history.return_value = (
        history or []
    )

    conversation_service.add_message.return_value = []

    return conversation_service


# =========================================================
# Mock RAG Service
# =========================================================

def create_rag_service():
    """
    Create a mocked RAG service.

    RAG is tested separately.
    """

    rag_service = MagicMock()

    rag_service.retrieve.return_value = []

    return rag_service


# =========================================================
# Mock Prompt Builder
# =========================================================

def create_prompt_builder():
    """
    Create a mocked PromptBuilder.

    The prompt is generated dynamically from the
    question and user context.
    """

    prompt_builder = MagicMock()

    def build_prompt(
        question,
        results,
        user_context=None,
    ):
        if user_context is not None:
            profile = (
                f"Goal: {user_context.goal}\n"
                f"Level: {user_context.level}\n"
                f"KYC Status: {user_context.kycStatus}\n"
                f"Holding Summary: "
                f"{user_context.holdingSummary}"
            )
        else:
            profile = (
                "[No user profile context was provided.]"
            )

        return (
            "SYSTEM INSTRUCTIONS:\n"
            "Answer only using the provided context.\n\n"
            "USER PROFILE:\n"
            f"{profile}\n\n"
            "KNOWLEDGE CONTEXT:\n"
            "[No relevant knowledge context was retrieved.]\n\n"
            "USER QUESTION:\n"
            f"{question}\n\n"
            "ANSWER:"
        )

    prompt_builder.build.side_effect = build_prompt

    return prompt_builder


# =========================================================
# Create ChatService
# =========================================================

def create_chat_service(
    llm_response=(
        "An ETF is an exchange-traded fund."
    ),
    history=None,
):
    """
    Create a completely isolated ChatService.

    No PostgreSQL is used.
    No real Redis is used.
    """

    llm_provider = MagicMock()

    llm_provider.generate = AsyncMock(
        return_value=llm_response
    )

    async def fake_stream(messages):
        yield llm_response

    llm_provider.stream = fake_stream

    rag_service = create_rag_service()

    prompt_builder = create_prompt_builder()

    conversation_service = (
        create_conversation_service(
            history=history
        )
    )

    service = ChatService(
        llm_provider=llm_provider,
        rag_service=rag_service,
        prompt_builder=prompt_builder,
        conversation_service=conversation_service,
    )

    return (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    )


# =========================================================
# Normal Question
# =========================================================

@pytest.mark.anyio
async def test_normal_question_is_processed():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message="What is an ETF?",
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "success"

    assert response.responseId is not None

    assert response.message == (
        "An ETF is an exchange-traded fund."
    )

    rag_service.retrieve.assert_called_once_with(
        "What is an ETF?"
    )

    prompt_builder.build.assert_called_once()

    llm_provider.generate.assert_called_once()


# =========================================================
# Personal Advice Must Be Blocked
# =========================================================

@pytest.mark.anyio
async def test_personal_advice_is_blocked():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message="Which stock should I buy?",
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "blocked"

    assert response.responseId is None

    assert response.category == (
        "personal_advice"
    )

    llm_provider.generate.assert_not_called()

    rag_service.retrieve.assert_not_called()

    prompt_builder.build.assert_not_called()


# =========================================================
# Another Personal Investment Decision
# =========================================================

@pytest.mark.anyio
async def test_personal_investment_decision_is_blocked():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message=(
            "Should I invest all my money "
            "in this stock?"
        ),
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "blocked"

    assert response.responseId is None

    llm_provider.generate.assert_not_called()

    rag_service.retrieve.assert_not_called()

    prompt_builder.build.assert_not_called()


# =========================================================
# RAG Is Called
# =========================================================

@pytest.mark.anyio
async def test_rag_context_is_used():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message="What is diversification?",
    )

    await service.process_chat(
        request
    )

    rag_service.retrieve.assert_called_once_with(
        "What is diversification?"
    )

    prompt_builder.build.assert_called_once()

    call_kwargs = (
        prompt_builder.build.call_args.kwargs
    )

    assert call_kwargs["question"] == (
        "What is diversification?"
    )

    assert call_kwargs["results"] == []

    assert call_kwargs["user_context"] is None

    llm_provider.generate.assert_called_once()


# =========================================================
# LLM Response Is Returned
# =========================================================

@pytest.mark.anyio
async def test_llm_response_is_returned_to_client():

    expected_response = (
        "Diversification means spreading "
        "investments across different assets."
    )

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service(
        llm_response=expected_response
    )

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message="What is diversification?",
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "success"

    assert response.message == (
        expected_response
    )

    assert response.responseId is not None

    rag_service.retrieve.assert_called_once()

    prompt_builder.build.assert_called_once()

    llm_provider.generate.assert_called_once()


# =========================================================
# Empty LLM Response
# =========================================================

@pytest.mark.anyio
async def test_empty_llm_response_is_blocked():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service(
        llm_response=""
    )

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message="What is an ETF?",
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "blocked"

    assert response.responseId is None

    assert (
        "empty response"
        in response.message.lower()
    )


# =========================================================
# Unsafe Response Is Blocked
# =========================================================

@pytest.mark.anyio
async def test_unsafe_llm_response_is_blocked():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service(
        llm_response=(
            "You are guaranteed a return "
            "from this investment."
        )
    )

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message=(
            "Tell me about this investment."
        ),
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "blocked"

    assert response.responseId is None

    assert response.category == (
        "response_validation"
    )

    llm_provider.generate.assert_called_once()


# =========================================================
# Database Independent
# =========================================================

@pytest.mark.anyio
async def test_chat_is_database_independent():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    request = ChatRequest(
        userId="any_user",
        sessionId="any_session",
        message="What is an ETF?",
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "success"

    assert response.message

    assert response.responseId

    llm_provider.generate.assert_called_once()


# =========================================================
# User Profile Is Passed to PromptBuilder
# =========================================================

@pytest.mark.anyio
async def test_user_profile_is_passed_to_prompt_builder():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    user_context = UserContext(
        goal="RETIREMENT_TEST_123",
        level="BEGINNER_TEST_456",
        kycStatus="VERIFIED_TEST_789",
        holdingSummary="HOLDINGS_TEST_ABC",
    )

    request = ChatRequest(
        userId="profile_test_user",
        sessionId="profile_test_session",
        message="Explain investing for me.",
        userContext=user_context,
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "success"

    prompt_builder.build.assert_called_once()

    call_kwargs = (
        prompt_builder.build.call_args.kwargs
    )

    assert call_kwargs["user_context"] == (
        user_context
    )


# =========================================================
# User Profile Is Actually Injected
# =========================================================

@pytest.mark.anyio
async def test_user_profile_is_injected_into_llm_prompt():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    user_context = UserContext(
        goal="RETIREMENT_TEST_123",
        level="BEGINNER_TEST_456",
        kycStatus="VERIFIED_TEST_789",
        holdingSummary="HOLDINGS_TEST_ABC",
    )

    request = ChatRequest(
        userId="profile_test_user",
        sessionId="profile_test_session",
        message="Explain investing for me.",
        userContext=user_context,
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "success"

    messages = (
        llm_provider.generate.call_args.args[0]
    )

    prompt = messages[-1]["content"]

    assert "USER PROFILE:" in prompt

    assert (
        "Goal: RETIREMENT_TEST_123"
        in prompt
    )

    assert (
        "Level: BEGINNER_TEST_456"
        in prompt
    )

    assert (
        "KYC Status: VERIFIED_TEST_789"
        in prompt
    )

    assert (
        "Holding Summary: HOLDINGS_TEST_ABC"
        in prompt
    )

    assert "USER QUESTION:" in prompt

    assert (
        "Explain investing for me."
        in prompt
    )

    assert prompt.index(
        "USER PROFILE:"
    ) < prompt.index(
        "USER QUESTION:"
    )


# =========================================================
# No Profile Context
# =========================================================

@pytest.mark.anyio
async def test_chat_works_without_user_profile():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message="What is an ETF?",
        userContext=None,
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "success"

    prompt_builder.build.assert_called_once()

    call_kwargs = (
        prompt_builder.build.call_args.kwargs
    )

    assert call_kwargs["user_context"] is None


# =========================================================
# Conversation History Is Used
# =========================================================

@pytest.mark.anyio
async def test_conversation_history_is_used():

    history = [
        {
            "role": "user",
            "content": "What is an ETF?",
        },
        {
            "role": "assistant",
            "content": (
                "An ETF is an exchange-traded fund."
            ),
        },
    ]

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service(
        history=history
    )

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message="How does it work?",
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "success"

    conversation_service.get_history.assert_called_once_with(
        user_id="test_user",
        session_id="test_session",
    )

    messages = (
        llm_provider.generate.call_args.args[0]
    )

    assert messages[0]["content"] == (
        "What is an ETF?"
    )

    assert messages[1]["content"] == (
        "An ETF is an exchange-traded fund."
    )

    assert len(messages) == 3

    assert "USER QUESTION:" in (
        messages[2]["content"]
    )

    assert (
        "How does it work?"
        in messages[2]["content"]
    )


# =========================================================
# Latest 10 Messages
# =========================================================

@pytest.mark.anyio
async def test_conversation_history_uses_latest_messages():

    history = [
        {
            "role": "user",
            "content": f"Message {i}",
        }
        for i in range(10)
    ]

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service(
        history=history
    )

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message="New question",
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "success"

    messages = (
        llm_provider.generate.call_args.args[0]
    )

    assert len(messages) == 11

    assert messages[0]["content"] == (
        "Message 0"
    )

    assert messages[9]["content"] == (
        "Message 9"
    )

    assert "USER QUESTION:" in (
        messages[10]["content"]
    )

    assert (
        "New question"
        in messages[10]["content"]
    )


# =========================================================
# Conversation Messages Are Stored
# =========================================================

@pytest.mark.anyio
async def test_conversation_messages_are_stored():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    request = ChatRequest(
        userId="test_user",
        sessionId="test_session",
        message="What is an ETF?",
    )

    response = await service.process_chat(
        request
    )

    assert response.status == "success"

    assert (
        conversation_service.add_message.call_count
        == 2
    )

    calls = (
        conversation_service.add_message.call_args_list
    )

    # User message
    assert calls[0].kwargs == {
        "user_id": "test_user",
        "session_id": "test_session",
        "role": "user",
        "content": "What is an ETF?",
    }

    # Assistant message
    assert calls[1].kwargs["user_id"] == (
        "test_user"
    )

    assert calls[1].kwargs["session_id"] == (
        "test_session"
    )

    assert calls[1].kwargs["role"] == (
        "assistant"
    )

    assert calls[1].kwargs["content"] == (
        "An ETF is an exchange-traded fund."
    )


# =========================================================
# Different Sessions Are Isolated
# =========================================================

@pytest.mark.anyio
async def test_different_sessions_use_different_history_keys():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    request = ChatRequest(
        userId="test_user",
        sessionId="session_one",
        message="What is an ETF?",
    )

    await service.process_chat(
        request
    )

    conversation_service.get_history.assert_called_once_with(
        user_id="test_user",
        session_id="session_one",
    )

    conversation_service.get_history.reset_mock()

    request_two = ChatRequest(
        userId="test_user",
        sessionId="session_two",
        message="What is diversification?",
    )

    await service.process_chat(
        request_two
    )

    conversation_service.get_history.assert_called_once_with(
        user_id="test_user",
        session_id="session_two",
    )


# =========================================================
# Streaming
# =========================================================

@pytest.mark.anyio
async def test_stream_chat_returns_llm_response():

    (
        service,
        llm_provider,
        rag_service,
        prompt_builder,
        conversation_service,
    ) = create_chat_service()

    request = ChatRequest(
        userId="stream_user",
        sessionId="stream_session",
        message="What is an ETF?",
    )

    chunks = []

    async for chunk in service.stream_chat(
        request
    ):
        chunks.append(chunk)

    result = "".join(chunks)

    assert (
        "An ETF is an exchange-traded fund."
        in result
    )

    rag_service.retrieve.assert_called_once_with(
        "What is an ETF?"
    )