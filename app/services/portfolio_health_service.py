from typing import Any

from app.services.llm.gemini_provider import GeminiProvider
from app.services.response_validator import validate_response


class PortfolioHealthService:
    """
    Generates a plain-English portfolio health report
    from numeric portfolio analytics.

    This service does not directly access PostgreSQL.
    """

    def __init__(
        self,
        llm_provider: GeminiProvider,
    ) -> None:
        self.llm_provider = llm_provider

    @staticmethod
    def build_prompt(
        analytics: dict[str, Any],
    ) -> str:
        """
        Build the prompt sent to Gemini.
        """

        return f"""
You are a financial education assistant.

Generate a concise portfolio health report using ONLY
the portfolio analytics supplied below.

Do not invent financial facts or market data.

Do not provide personalized buy, sell, or portfolio
allocation recommendations.

Do not guarantee investment returns.

Explain the portfolio objectively.

Include:
- total invested amount
- current portfolio value
- total profit or loss
- profit/loss percentage
- number of holdings
- notable holding-level observations

If the available data is insufficient for an observation,
clearly say so.

PORTFOLIO ANALYTICS:

User ID:
{analytics.get("userId")}

Number of Holdings:
{analytics.get("holdingsCount")}

Total Invested:
{analytics.get("totalInvested")}

Current Portfolio Value:
{analytics.get("currentValue")}

Total P&L:
{analytics.get("totalPnl")}

P&L Percentage:
{analytics.get("pnlPercentage")}

Holding Details:
{analytics.get("holdings")}

PORTFOLIO HEALTH REPORT:
""".strip()

    async def generate_report(
        self,
        analytics: dict[str, Any],
    ) -> str:
        """
        Generate a validated portfolio health report.
        """

        if not isinstance(
            analytics,
            dict,
        ):
            raise TypeError(
                "analytics must be a dictionary"
            )

        prompt = self.build_prompt(
            analytics
        )

        response = await self.llm_provider.generate(
            [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        if not response or not response.strip():
            raise RuntimeError(
                "Portfolio health report is empty"
            )

        validation = validate_response(
            response
        )

        if not validation.valid:
            raise RuntimeError(
                validation.message
                or (
                    "Portfolio health report "
                    "failed response validation"
                )
            )

        return response.strip()