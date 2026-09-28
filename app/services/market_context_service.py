from datetime import date, datetime, timedelta, timezone

from app.schemas.market_context import (
    MarketContextResponse,
    MarketIndexContext,
    MarketNewsContext,
)
from app.services.benchmark_service import BenchmarkService
from app.services.google_news_provider import GoogleNewsProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.news_cache_service import NewsCacheService
from app.services.news_sentiment_service import NewsSentimentService
from app.services.nse_market_data_provider import NSEMarketDataProvider


class MarketContextService:
    """
    Builds the structured market context for Task 6.

    Supported benchmark indices are obtained from the configured
    market-data provider. Recent market news is obtained from
    the configured news provider.

    This service does not access user-specific PostgreSQL data.
    """

    CACHE_KEY = "market-context"
    MARKET_NEWS_SYMBOL = "^NSEI"

    def __init__(
        self,
        benchmark_service: BenchmarkService | None = None,
        news_provider: GoogleNewsProvider | None = None,
        sentiment_service: NewsSentimentService | None = None,
    ) -> None:
        self.benchmark_service = (
            benchmark_service
            or BenchmarkService(
                market_data_provider=NSEMarketDataProvider()
            )
        )

        self.news_provider = (
            news_provider
            or GoogleNewsProvider()
        )

        self.sentiment_service = (
            sentiment_service
            or NewsSentimentService(
                llm_provider=GeminiProvider()
            )
        )

    def _get_supported_sector_indices(self) -> list[str]:
        """
        Get sector benchmark names from the configured
        market-data provider.

        The provider owns the benchmark definitions.
        This service does not maintain a duplicate list.
        """

        provider = getattr(
            self.benchmark_service,
            "market_data_provider",
            None,
        )

        index_symbols = getattr(
            provider,
            "INDEX_SYMBOLS",
            {},
        )

        if not isinstance(
            index_symbols,
            dict,
        ):
            return []

        return [
            str(name).strip()
            for name in index_symbols
            if str(name).strip()
            and str(name).strip().upper() != "NIFTY 50"
        ]

    def _get_latest_market_news_metadata(
        self,
    ) -> tuple[str | None, str | None]:
        """
        Perform a lightweight source-news check.

        No sentiment analysis is performed here.

        Returns:
            latest article identity and publication timestamp.
        """

        news = self.news_provider.get_news(
            symbol=self.MARKET_NEWS_SYMBOL,
            limit=10,
        )

        if not news:
            return None, None

        latest = max(
            news,
            key=lambda article: self._publication_timestamp(
                article.published_at
            ),
        )

        return (
            latest.url or latest.title,
            latest.published_at,
        )

    async def get_market_context(
        self,
    ) -> MarketContextResponse:

        # -------------------------------------------------
        # Check processed cache first.
        # -------------------------------------------------
        cached = NewsCacheService.get_news_cache(
            self.CACHE_KEY
        )

        # -------------------------------------------------
        # If cached data exists, perform only a lightweight
        # source freshness check.
        # -------------------------------------------------
        if cached is not None:
            try:
                (
                    latest_article_key,
                    latest_published_at,
                ) = self._get_latest_market_news_metadata()

                # No new article is available.
                # Keep and return the processed result.
                if not NewsCacheService.is_newer_article_available(
                    cached=cached,
                    latest_article_key=latest_article_key,
                    latest_published_at=latest_published_at,
                ):
                    cached_response = cached.get(
                        "articles"
                    )

                    if cached_response:
                        return MarketContextResponse.model_validate(
                            cached_response
                        )

            except RuntimeError:
                # If freshness checking fails, retain the
                # existing processed cache when possible.
                cached_response = cached.get(
                    "articles"
                )

                if cached_response:
                    return MarketContextResponse.model_validate(
                        cached_response
                    )

        today = date.today()

        # Use a 7-day window to ensure enough
        # trading-day observations are available,
        # even around weekends and market holidays.
        start_date = today - timedelta(days=7)

        indices: list[MarketIndexContext] = []

        # -------------------------------------------------
        # NIFTY 50 performance
        # -------------------------------------------------
        try:
            performance = (
                self.benchmark_service.get_nifty_50_performance(
                    start_date=start_date,
                    end_date=today,
                )
            )

            indices.append(
                MarketIndexContext(
                    name=performance.name,
                    returnPercentage=(
                        performance.return_percentage
                    ),
                )
            )

        except RuntimeError:
            pass

        # -------------------------------------------------
        # Sector index performance
        # -------------------------------------------------
        sector_indices = (
            self._get_supported_sector_indices()
        )

        for sector in sector_indices:
            try:
                performance = (
                    self.benchmark_service.get_sector_performance(
                        sector=sector,
                        start_date=start_date,
                        end_date=today,
                    )
                )

                indices.append(
                    MarketIndexContext(
                        name=performance.name,
                        returnPercentage=(
                            performance.return_percentage
                        ),
                    )
                )

            except (
                RuntimeError,
                ValueError,
            ):
                continue

        # -------------------------------------------------
        # Retrieve market news.
        #
        # This happens only when there is no valid cache
        # or a newer article has been detected.
        # -------------------------------------------------
        news = self.news_provider.get_news(
            symbol=self.MARKET_NEWS_SYMBOL,
            limit=10,
        )

        sentiments = (
            await self.sentiment_service.analyze(
                news
            )
        )

        sentiment_by_title = {
            item["title"]: item["sentiment"]
            for item in sentiments
        }

        news_context: list[MarketNewsContext] = []

        for article in news:
            news_context.append(
                MarketNewsContext(
                    title=article.title,
                    summary=article.summary,
                    source=article.source,
                    publishedAt=article.published_at,
                    url=article.url,
                    sentiment=sentiment_by_title.get(
                        article.title,
                        "neutral",
                    ),
                )
            )

        response = MarketContextResponse(
            asOf=datetime.now(
                timezone.utc
            ).isoformat(),
            indices=indices,
            news=news_context,
        )

        # -------------------------------------------------
        # Store processed market context together with
        # latest source article metadata.
        #
        # Redis keeps the complete result for 2 hours.
        # -------------------------------------------------
        latest_article_key = None
        latest_published_at = None

        if news:
            latest_article = max(
                news,
                key=lambda article: (
                    self._publication_timestamp(
                        article.published_at
                    )
                ),
            )

            latest_article_key = (
                latest_article.url
                or latest_article.title
            )

            latest_published_at = (
                latest_article.published_at
            )

        NewsCacheService.set_news_cache(
            cache_key=self.CACHE_KEY,
            articles=response.model_dump(),
            latest_article_key=latest_article_key,
            latest_published_at=latest_published_at,
        )

        return response

    @staticmethod
    def _parse_datetime(
        value: str,
    ) -> datetime | None:

        if not value:
            return None

        try:
            parsed = datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )

            if parsed.tzinfo is None:
                parsed = parsed.replace(
                    tzinfo=timezone.utc
                )

            return parsed

        except (
            ValueError,
            TypeError,
        ):
            return None

    @classmethod
    def _publication_timestamp(
        cls,
        value: str,
    ) -> float:

        parsed = cls._parse_datetime(value)

        if parsed is None:
            return 0.0

        return parsed.timestamp()