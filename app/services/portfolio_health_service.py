from typing import Any

from app.services.llm.gemini_provider import GeminiProvider
from app.services.response_validator import validate_response


class PortfolioHealthService:
    """
    Generates a plain-English portfolio health report
    from numeric portfolio analytics and structured market context.

    This service does not directly access PostgreSQL.
    It receives portfolio analytics and market context as JSON-compatible data.
    """

    def __init__(
        self,
        llm_provider: GeminiProvider,
    ) -> None:
        self.llm_provider = llm_provider

    @staticmethod
    def build_prompt(
        analytics: dict[str, Any],
        market_context: dict[str, Any] | None = None,
    ) -> str:
        """
        Build the prompt sent to Gemini.

        Portfolio analytics and market context are supplied dynamically
        as JSON-compatible data.
        """

        market_context = market_context or {}

        return f"""
You are a financial education assistant.

Generate a concise portfolio health report using ONLY
the portfolio analytics and market context supplied below.

Do not invent financial facts, market data, or news.

Do not provide personalized buy, sell, or portfolio
allocation recommendations.

Do not guarantee investment returns.

Explain the portfolio objectively.

Use the supplied market context only to provide relevant
context for understanding the portfolio's performance.

Include:

- total invested amount
- current portfolio value
- total profit or loss
- profit/loss percentage
- number of holdings
- notable holding-level observations
- relevant market context that may help explain the
  portfolio's overall performance
- relevant market news context when it is supported by
  the supplied news

If the available data is insufficient for an observation,
clearly say so.

PORTFOLIO ANALYTICS:

{analytics}

MARKET CONTEXT:

{market_context}

PORTFOLIO HEALTH REPORT:
""".strip()

    async def generate_report(
        self,
        analytics: dict[str, Any],
        market_context: dict[str, Any] | None = None,
    ) -> str:
        """
        Generate a validated portfolio health report.

        The service receives portfolio analytics and market
        context as JSON-compatible dictionaries and does not
        directly access PostgreSQL.
        """

        if not isinstance(
            analytics,
            dict,
        ):
            raise TypeError(
                "analytics must be a dictionary"
            )

        if market_context is not None and not isinstance(
            market_context,
            dict,
        ):
            raise TypeError(
                "market_context must be a dictionary"
            )

        prompt = self.build_prompt(
            analytics=analytics,
            market_context=market_context,
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