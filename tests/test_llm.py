import pytest

from app.services.llm.base import LLMProvider
from app.services.llm.mock_provider import MockLLMProvider


@pytest.mark.anyio
async def test_mock_provider_implements_llm_interface():

    provider = MockLLMProvider()

    assert isinstance(provider, LLMProvider)


@pytest.mark.anyio
async def test_mock_provider_generates_response():

    provider = MockLLMProvider()

    response = await provider.generate(
        [
            {
                "role": "user",
                "content": "What is an ETF?",
            }
        ]
    )

    assert "Mock LLM response" in response
    assert "What is an ETF?" in response


@pytest.mark.anyio
async def test_empty_messages_are_rejected():

    provider = MockLLMProvider()

    with pytest.raises(ValueError):
        await provider.generate([])


@pytest.mark.anyio
async def test_empty_user_message_is_rejected():

    provider = MockLLMProvider()

    with pytest.raises(ValueError):
        await provider.generate(
            [
                {
                    "role": "user",
                    "content": "   ",
                }
            ]
        )


@pytest.mark.anyio
async def test_last_message_must_be_user():

    provider = MockLLMProvider()

    with pytest.raises(ValueError):
        await provider.generate(
            [
                {
                    "role": "assistant",
                    "content": "Previous response",
                }
            ]
        )