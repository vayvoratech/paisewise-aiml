from typing import Any

from app.repositories.holdings_repository import (
    HoldingsRepository,
)
from app.schemas.portfolio_analytics import (
    HoldingAnalytics,
    PortfolioAnalyticsResponse,
)


class PortfolioAnalyticsService:
    """
    Calculates numeric portfolio analytics from
    the user's current holdings.

    Database access is kept inside HoldingsRepository.
    """

    def __init__(
        self,
        holdings_repository: HoldingsRepository | None = None,
    ) -> None:
        self.holdings_repository = (
            holdings_repository
            or HoldingsRepository()
        )

    @staticmethod
    def _to_float(value: Any) -> float:
        """
        Safely convert database numeric values
        such as Decimal/int/float into float.
        """
        if value is None:
            return 0.0

        return float(value)

    def calculate(
        self,
        user_id: str,
    ) -> PortfolioAnalyticsResponse:
        """
        Calculate portfolio-level and
        holding-level analytics.
        """

        if not user_id or not user_id.strip():
            raise ValueError(
                "user_id cannot be empty"
            )

        holdings = (
            self.holdings_repository.get_holdings(
                user_id.strip()
            )
        )

        analytics: list[HoldingAnalytics] = []

        total_invested = 0.0
        total_current_value = 0.0

        for holding in holdings:
            shares = self._to_float(
                holding.get("shares")
            )

            avg_price = self._to_float(
                holding.get("avg_price")
            )

            current_price = self._to_float(
                holding.get("current_price")
            )

            invested_value = (
                shares * avg_price
            )

            current_value = (
                shares * current_price
            )

            pnl = (
                current_value
                - invested_value
            )

            if invested_value > 0:
                pnl_percentage = (
                    pnl
                    / invested_value
                    * 100
                )
            else:
                pnl_percentage = 0.0

            total_invested += invested_value
            total_current_value += current_value

            analytics.append(
                HoldingAnalytics(
                    symbol=str(
                        holding.get("symbol")
                        or ""
                    ),
                    shares=shares,
                    avg_price=avg_price,
                    current_price=current_price,
                    invested_value=round(
                        invested_value,
                        2,
                    ),
                    current_value=round(
                        current_value,
                        2,
                    ),
                    pnl=round(
                        pnl,
                        2,
                    ),
                    pnl_percentage=round(
                        pnl_percentage,
                        2,
                    ),
                )
            )

        total_pnl = (
            total_current_value
            - total_invested
        )

        if total_invested > 0:
            total_pnl_percentage = (
                total_pnl
                / total_invested
                * 100
            )
        else:
            total_pnl_percentage = 0.0

        return PortfolioAnalyticsResponse(
            userId=user_id,
            holdingsCount=len(analytics),
            totalInvested=round(
                total_invested,
                2,
            ),
            currentValue=round(
                total_current_value,
                2,
            ),
            totalPnl=round(
                total_pnl,
                2,
            ),
            pnlPercentage=round(
                total_pnl_percentage,
                2,
            ),
            holdings=analytics,
        )