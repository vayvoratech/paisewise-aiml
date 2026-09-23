import pytest
from unittest.mock import AsyncMock

from app.services.reengagement_llm_service import ReengagementLLMService
from app.services.reengagement_message_service import (
    ReengagementMessageRequest,
)


@pytest.mark.asyncio
async def test_generates_ai_reengagement_message() -> None:
    llm_provider = AsyncMock()
    llm_provider.generate.return_value = (
        "You're almost there! Complete your risk profile to continue."
    )

    service = ReengagementLLMService(llm_provider)

    request = ReengagementMessageRequest(
        userId="user-123",
        churnScore=0.85,
        journeyContext={
            "completed_steps": ["registration"],
            "incomplete_steps": ["risk profiling"],
        },
    )

    result = await service.generate(request)

    assert result.userId == "user-123"
    assert result.message == (
        "You're almost there! Complete your risk profile to continue."
    )
    assert result.generatedBy == "ai"

    llm_provider.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_llm_empty_response_raises_error() -> None:
    llm_provider = AsyncMock()
    llm_provider.generate.return_value = ""

    service = ReengagementLLMService(llm_provider)

    request = ReengagementMessageRequest(
        userId="user-123",
        churnScore=0.85,
        journeyContext={
            "incomplete_steps": ["risk profiling"],
        },
    )

    with pytest.raises(
        RuntimeError,
        match="LLM returned an empty re-engagement message",
    ):
        await service.generate(request)


@pytest.mark.asyncio
async def test_llm_prompt_contains_journey_context() -> None:
    llm_provider = AsyncMock()
    llm_provider.generate.return_value = "Continue your investment journey."

    service = ReengagementLLMService(llm_provider)

    request = ReengagementMessageRequest(
        userId="user-456",
        churnScore=0.91,
        journeyContext={
            "completed_steps": ["registration"],
            "incomplete_steps": ["risk profiling", "first investment"],
        },
    )

    await service.generate(request)

    messages = llm_provider.generate.call_args.args[0]

    user_message = messages[1]["content"]

    assert "user-456" in user_message
    assert "0.91" in user_message
    assert "risk profiling" in user_message
    assert "first investment" in user_message