import importlib
import os


if os.getenv("APP_ENV", "").lower() != "staging":
    raise RuntimeError("Set APP_ENV=staging to use the test app.")

if os.getenv("TASK14_LOADTEST") != "1":
    raise RuntimeError("Set TASK14_LOADTEST=1 to use the test app.")


class Task14LoadTestProvider:
    """Fixed-response provider for local load testing; no Gemini calls."""

    model = "task14-fixed-mock"

    def __init__(self, cost_service=None):
        print(
            "[TASK14 LOAD TEST] Fixed mock provider active; "
            "chat requests will not call Gemini."
        )

    async def generate(self, messages: list[dict[str, str]]) -> str:
        return (
            "Diversification spreads investments across different assets. "
            "It can reduce concentration risk, but it does not guarantee "
            "profit or prevent losses."
        )

    async def stream(self, messages: list[dict[str, str]]):
        response = await self.generate(messages)
        for word in response.split():
            yield word + " "


# Substitute the provider before the normal app imports the chat route.
gemini_module = importlib.import_module(
    "app.services.llm.gemini_provider"
)
gemini_module.GeminiProvider = Task14LoadTestProvider

from app.main import app  # noqa: E402