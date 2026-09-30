import pytest
from unittest.mock import Mock

from app.schemas.chat import ChatRequest, UserContext
from app.services.chat_service import ChatService


@pytest.mark.anyio
async def test_previous_conversation_history_is_included_in_messages():
    llm_provider = Mock()
    rag_service = Mock()
    prompt_builder = Mock()
    conversation_service = Mock()

    rag_service.retrieve.return_value = []

    prompt_builder.build.return_value = (
        "SYSTEM INSTRUCTIONS:\n"
        "Answer using the provided context.\n\n"
        "USER QUESTION:\n"
        "What about that?"
    )

    conversation_service.get_profile.return_value = None
    conversation_service.get_history.return_value = [
        {
            "role": "user",
            "content": "What is an ETF?",
        },
        {
            "role": "assistant",
            "content": "An ETF is an exchange-traded fund.",
        },
    ]

    service = ChatService(
        llm_provider=llm_provider,
        rag_service=rag_service,
        prompt_builder=prompt_builder,
        conversation_service=conversation_service,
    )

    request = ChatRequest(
        userId="continuity-test-user",
        sessionId="continuity-test-session",
        message="What about that?",
    )

    messages = await service._build_messages(request)

    assert len(messages) == 3

    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What is an ETF?"

    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "An ETF is an exchange-traded fund."

    assert messages[2]["role"] == "user"
    assert "What about that?" in messages[2]["content"]

    conversation_service.get_history.assert_called_once_with(
        user_id="continuity-test-user",
        session_id="continuity-test-session",
    )


@pytest.mark.anyio
async def test_user_profile_can_be_restored_for_follow_up_request():
    llm_provider = Mock()
    rag_service = Mock()
    prompt_builder = Mock()
    conversation_service = Mock()

    rag_service.retrieve.return_value = []

    stored_profile = {
        "goal": "Learn investing",
        "level": "beginner",
        "kycStatus": "verified",
        "holdingSummary": "Mutual funds",
    }

    conversation_service.get_profile.return_value = stored_profile
    conversation_service.get_history.return_value = []

    prompt_builder.build.return_value = "test prompt"

    service = ChatService(
        llm_provider=llm_provider,
        rag_service=rag_service,
        prompt_builder=prompt_builder,
        conversation_service=conversation_service,
    )

    request = ChatRequest(
        userId="continuity-test-user",
        sessionId="continuity-test-session",
        message="Explain diversification.",
        userContext=None,
    )

    messages = await service._build_messages(request)

    conversation_service.get_profile.assert_called_once_with(
        user_id="continuity-test-user",
        session_id="continuity-test-session",
    )

    prompt_builder.build.assert_called_once()

    kwargs = prompt_builder.build.call_args.kwargs
    restored_context = kwargs["user_context"]

    assert isinstance(restored_context, UserContext)
    assert restored_context.goal == "Learn investing"
    assert restored_context.level == "beginner"
    assert restored_context.kycStatus == "verified"
    assert restored_context.holdingSummary == "Mutual funds"

    assert messages[-1]["role"] == "user"