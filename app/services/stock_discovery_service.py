from app.repositories.holdings_repository import HoldingsRepository
from app.repositories.stocks_repository import StocksRepository
from app.services.sector_metadata_provider import (
    SectorMetadataProvider,
)
from app.services.sector_news_service import SectorNewsService


class StockDiscoveryService:
    """
    Builds stock-discovery context using the user's portfolio.

    Flow:
        User portfolio
            ↓
        Holdings
            ↓
        Stock market data
            ↓
        Dynamic sector metadata
            ↓
        Sector news
            ↓
        JSON-ready discovery response
    """

    def __init__(
        self,
        holdings_repository: HoldingsRepository | None = None,
        stocks_repository: StocksRepository | None = None,
        sector_metadata_provider: SectorMetadataProvider | None = None,
        sector_news_service: SectorNewsService | None = None,
    ) -> None:
        self.holdings_repository = (
            holdings_repository or HoldingsRepository()
        )

        self.stocks_repository = (
            stocks_repository or StocksRepository()
        )

        self.sector_metadata_provider = (
            sector_metadata_provider
            or SectorMetadataProvider()
        )

        self.sector_news_service = (
            sector_news_service
            or SectorNewsService()
        )

    async def discover(
        self,
        user_id: str,
    ) -> list[dict]:

        if not user_id or not user_id.strip():
            raise ValueError(
                "user_id cannot be empty"
            )

        holdings = (
            self.holdings_repository.get_holdings(
                user_id.strip()
            )
        )

        if not holdings:
            return []

        stocks = self.stocks_repository.get_stocks()

        stocks_by_symbol = {
            str(stock.get("symbol", "")).upper(): stock
            for stock in stocks
        }

        discovered: list[dict] = []

        sector_news_cache: dict[str, list] = {}

        for holding in holdings:
            symbol = str(
                holding.get("symbol") or ""
            ).strip().upper()

            if not symbol:
                continue

            stock = stocks_by_symbol.get(symbol)

            if stock is None:
                continue

            sector_info = (
                self.sector_metadata_provider.get_sector(
                    symbol
                )
            )

            if sector_info is None:
                continue

            sector = sector_info.sector

            if sector not in sector_news_cache:
                sector_news_cache[sector] = (
                    await self.sector_news_service.get_news(
                        sector=sector,
                        limit=5,
                    )
                )

            sector_news = sector_news_cache[sector]

            discovered.append(
                {
                    "symbol": symbol,
                    "companyName": (
                        sector_info.company_name
                    ),
                    "sector": sector,
                    "price": stock.get("price"),
                    "changePct": stock.get(
                        "change_pct"
                    ),
                    "emoji": stock.get("emoji"),
                    "news": [
                        {
                            "title": article.title,
                            "summary": article.summary,
                            "source": article.source,
                            "publishedAt": (
                                article.published_at
                            ),
                            "url": article.url,
                            "sentiment": (
                                article.sentiment
                                or "neutral"
                            ),
                        }
                        for article in sector_news
                    ],
                }
            )

        return discovered