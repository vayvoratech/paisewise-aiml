from typing import AsyncIterator

from app.services.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider used for testing.

    Implements both:
        - generate() for complete responses
        - stream() for streaming responses
    """

    async def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate a deterministic mock response.
        """

        # Validate messages
        if not messages:
            raise ValueError(
                "messages cannot be empty"
            )

        # Get the last message
        last_message = messages[-1]

        # Last message must be from the user
        if last_message.get("role") != "user":
            raise ValueError(
                "last message must have role 'user'"
            )

        # Get user content
        content = last_message.get(
            "content",
            "",
        )

        # Reject empty user messages
        if not content.strip():
            raise ValueError(
                "user message cannot be empty"
            )

        # Deterministic mock response
        return f"Mock LLM response: {content}"

    async def stream(
        self,
        messages: list[dict[str, str]],
    ) -> AsyncIterator[str]:
        """
        Stream the mock response in small chunks.

        This is used to test the streaming architecture
        without calling a real LLM provider.
        """

        response = await self.generate(
            messages
        )

        # Stream word by word
        for word in response.split():
            yield word + " "