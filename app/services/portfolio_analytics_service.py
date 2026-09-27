from typing import Any

from app.repositories.holdings_repository import HoldingsRepository
from app.schemas.portfolio_analytics import (
    HoldingAnalytics,
    PortfolioAnalyticsResponse,
)
from app.services.market_service import get_market


class PortfolioAnalyticsService:
    """
    Calculates portfolio analytics from the user's holdings.
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
        if value is None:
            return 0.0

        return float(value)

    @staticmethod
    def _get_current_price(
        symbol: str,
        current_price: Any,
    ) -> float:
        price = PortfolioAnalyticsService._to_float(
            current_price
        )

        if price > 0:
            return price

        if not symbol:
            return 0.0

        try:
            quote = get_market(symbol)
            market_price = quote.get("price") if quote else None
            return PortfolioAnalyticsService._to_float(
                market_price
            )
        except Exception:
            return 0.0

    def calculate(
        self,
        user_id: str,
    ) -> PortfolioAnalyticsResponse:

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
            symbol = str(
                holding.get("symbol")
                or ""
            )

            shares = self._to_float(
                holding.get("shares")
            )

            avg_price = self._to_float(
                holding.get("avg_price")
            )

            current_price = self._get_current_price(
                symbol,
                holding.get("current_price"),
            )

            invested_value = shares * avg_price
            current_value = shares * current_price

            pnl = current_value - invested_value

            if invested_value > 0:
                pnl_percentage = (
                    pnl / invested_value * 100
                )
            else:
                pnl_percentage = 0.0

            total_invested += invested_value
            total_current_value += current_value

            analytics.append(
                HoldingAnalytics(
                    symbol=symbol,
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
