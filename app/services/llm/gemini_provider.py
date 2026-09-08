import os
from typing import AsyncIterator

from google import genai

from app.services.llm.base import LLMProvider


class GeminiProvider(LLMProvider):

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )

    async def generate(
        self,
        messages: list[dict],
    ) -> str:

        prompt = self._build_prompt(messages)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response"
            )

        return response.text

    async def stream(
        self,
        messages: list[dict],
    ) -> AsyncIterator[str]:

        prompt = self._build_prompt(messages)

        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    @staticmethod
    def _build_prompt(
        messages: list[dict],
    ) -> str:

        parts = []

        for message in messages:

            role = message.get(
                "role",
                "user",
            )

            content = message.get(
                "content",
                "",
            )

            parts.append(
                f"{role.upper()}: {content}"
            )

        return "\n".join(parts)