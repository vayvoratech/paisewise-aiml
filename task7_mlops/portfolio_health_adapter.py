from typing import Any

from app.services.portfolio_health_service import PortfolioHealthService
from app.services.llm.gemini_provider import GeminiProvider


class PortfolioHealthAdapter:
    """
    MLOps adapter for the existing Portfolio Health component.

    The original portfolio_health_service.py is not modified.
    """

    model_name = "Portfolio Health"
    model_version = "v1"
    model_type = "llm_based"

    def __init__(self, llm_provider: GeminiProvider) -> None:
        self.service = PortfolioHealthService(llm_provider)

    async def predict(
        self,
        analytics: dict[str, Any],
        market_context: dict[str, Any] | None = None,
    ) -> str:
        return await self.service.generate_report(
            analytics=analytics,
            market_context=market_context,
        )

    def metadata(self) -> dict[str, str]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_type": self.model_type,
        }