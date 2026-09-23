from app.services.llm.gemini_provider import GeminiProvider
from app.services.reengagement_message_service import (
    ReengagementMessageRequest,
    ReengagementMessageResponse,
)


class ReengagementLLMService:
    """
    Generates personalized churn re-engagement messages using the
    existing Gemini provider.

    The service receives JSON-style structured context and does not
    access PostgreSQL or user data directly.
    """

    def __init__(self, llm_provider: GeminiProvider) -> None:
        self.llm_provider = llm_provider

    async def generate(
        self,
        request: ReengagementMessageRequest,
    ) -> ReengagementMessageResponse:
        user_id = request.userId.strip()

        if not user_id:
            raise ValueError("userId cannot be empty")

        prompt = self._build_prompt(request)

        response = await self.llm_provider.generate(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a financial investment platform "
                        "re-engagement assistant. "
                        "Create a short, helpful and personalized "
                        "message encouraging the user to continue "
                        "their incomplete investment journey. "
                        "Do not make investment guarantees or promises. "
                        "Return only the message text."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )

        message = response.strip()

        if not message:
            raise RuntimeError(
                "LLM returned an empty re-engagement message"
            )

        return ReengagementMessageResponse(
            userId=user_id,
            message=message,
            generatedBy="ai",
        )

    @staticmethod
    def _build_prompt(
        request: ReengagementMessageRequest,
    ) -> str:
        return (
            f"User ID: {request.userId}\n"
            f"Churn score: {request.churnScore}\n"
            f"Journey context: {request.journeyContext}\n\n"
            "Generate one concise personalized re-engagement message "
            "based on the incomplete journey steps."
        )