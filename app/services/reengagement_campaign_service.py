from app.services.reengagement_ab_test_service import (
    ReengagementABTestService,
)
from app.services.reengagement_llm_service import (
    ReengagementLLMService,
)
from app.services.reengagement_message_service import (
    ReengagementMessageRequest,
    ReengagementMessageService,
)


class ReengagementCampaignService:
    """
    Selects the re-engagement message variant for a high-risk user.

    High-risk threshold:
        churn_score > 0.7

    Variants:
        ai       -> Gemini-generated message
        template -> deterministic template message

    This service does not access PostgreSQL directly.
    """

    HIGH_RISK_THRESHOLD = 0.7

    def __init__(
        self,
        ab_test_service: ReengagementABTestService | None = None,
        template_service: ReengagementMessageService | None = None,
        llm_service: ReengagementLLMService | None = None,
    ) -> None:
        self.ab_test_service = (
            ab_test_service or ReengagementABTestService()
        )
        self.template_service = (
            template_service or ReengagementMessageService()
        )
        self.llm_service = llm_service

    async def create_message(
        self,
        request: ReengagementMessageRequest,
    ):
        if request.churnScore <= self.HIGH_RISK_THRESHOLD:
            return None

        assignment = self.ab_test_service.assign(request.userId)

        if assignment.variant == ReengagementABTestService.AI_VARIANT:
            if self.llm_service is None:
                raise RuntimeError(
                    "LLM service is required for AI variant"
                )

            return await self.llm_service.generate(request)

        return self.template_service.generate(request)