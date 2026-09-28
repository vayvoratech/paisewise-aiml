from datetime import datetime, timedelta, timezone

from app.services.google_news_provider import GoogleNewsProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.news_provider import NewsArticle
from app.services.news_sentiment_service import (
    NewsSentimentService,
)
from app.services.yfinance_news_provider import (
    YFinanceNewsProvider,
)


class StockNewsService:
    """
    Retrieves recent stock news using multiple providers.

    Provider priority:
        1. Google News
        2. Yahoo Finance

    News is searched dynamically using the supplied stock
    symbol or dynamically resolved company name.

    Only recent articles are returned.

    Sentiment is preserved when supplied by a provider;
    otherwise it is generated using the LLM.
    """

    RECENT_NEWS_DAYS = 7

    def __init__(
        self,
        google_provider: GoogleNewsProvider | None = None,
        yahoo_provider: YFinanceNewsProvider | None = None,
        sentiment_service: NewsSentimentService | None = None,
    ) -> None:

        self.google_provider = (
            google_provider
            or GoogleNewsProvider()
        )

        self.yahoo_provider = (
            yahoo_provider
            or YFinanceNewsProvider()
        )

        self.sentiment_service = (
            sentiment_service
            or NewsSentimentService(
                llm_provider=GeminiProvider()
            )
        )

    async def get_news(
        self,
        symbol: str,
        limit: int = 3,
    ) -> list[NewsArticle]:

        if not symbol or not symbol.strip():
            raise ValueError(
                "symbol cannot be empty"
            )

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

        normalized_symbol = (
            symbol.strip().upper()
        )

        candidate_limit = max(
            limit * 3,
            10,
        )

        # ---------------------------------------------
        # 1. Google News
        # ---------------------------------------------
        try:
            articles = self.google_provider.get_news(
                normalized_symbol,
                limit=candidate_limit,
            )

            selected = self._select_articles(
                normalized_symbol,
                articles,
                limit,
            )

            if selected:
                return await self._ensure_sentiment(
                    selected
                )

        except RuntimeError:
            pass

        # ---------------------------------------------
        # 2. Yahoo Finance fallback
        # ---------------------------------------------
        articles = self.yahoo_provider.get_news(
            normalized_symbol,
            limit=candidate_limit,
        )

        selected = self._select_articles(
            normalized_symbol,
            articles,
            limit,
        )

        return await self._ensure_sentiment(
            selected
        )

    def get_latest_article_metadata(
        self,
        symbol: str,
    ) -> tuple[str | None, str | None]:
        """
        Return metadata for the latest available source article.

        This method is intentionally lightweight.
        It does not run sentiment analysis or other processing.

        It is used only to determine whether cached news
        needs to be refreshed.
        """

        if not symbol or not symbol.strip():
            raise ValueError(
                "symbol cannot be empty"
            )

        normalized_symbol = symbol.strip().upper()

        candidate_limit = 10

        # ---------------------------------------------
        # 1. Google News
        # ---------------------------------------------
        try:
            articles = self.google_provider.get_news(
                normalized_symbol,
                limit=candidate_limit,
            )

            if articles:
                latest = max(
                    articles,
                    key=lambda article: self._publication_timestamp(
                        article.published_at
                    ),
                )

                return (
                    latest.url or latest.title,
                    latest.published_at,
                )

        except RuntimeError:
            pass

        # ---------------------------------------------
        # 2. Yahoo Finance fallback
        # ---------------------------------------------
        articles = self.yahoo_provider.get_news(
            normalized_symbol,
            limit=candidate_limit,
        )

        if not articles:
            return None, None

        latest = max(
            articles,
            key=lambda article: self._publication_timestamp(
                article.published_at
            ),
        )

        return (
            latest.url or latest.title,
            latest.published_at,
        )

    def _select_articles(
        self,
        symbol: str,
        articles: list[NewsArticle],
        limit: int,
    ) -> list[NewsArticle]:

        if not articles:
            return []

        now = datetime.now(timezone.utc)

        recent_cutoff = (
            now
            - timedelta(
                days=self.RECENT_NEWS_DAYS
            )
        )

        recent_articles: list[NewsArticle] = []

        for article in articles:

            published = self._parse_datetime(
                article.published_at
            )

            if (
                published is not None
                and published >= recent_cutoff
            ):
                recent_articles.append(article)

        recent_articles.sort(
            key=lambda article: (
                self._relevance_score(
                    article,
                    symbol,
                ),
                self._publication_timestamp(
                    article.published_at
                ),
            ),
            reverse=True,
        )

        return recent_articles[:limit]

    @staticmethod
    def _relevance_score(
        article: NewsArticle,
        symbol: str,
    ) -> int:

        title = article.title.lower()
        summary = article.summary.lower()
        text = f"{title} {summary}"

        normalized_symbol = symbol.lower()

        score = 0

        # Direct symbol mention.
        if normalized_symbol in title:
            score += 20

        if normalized_symbol in summary:
            score += 10

        # Financial/investment relevance.
        financial_keywords = {
            "stock": 8,
            "stocks": 8,
            "share": 8,
            "shares": 8,
            "market": 6,
            "trading": 6,
            "traded": 6,
            "earnings": 8,
            "results": 8,
            "revenue": 7,
            "profit": 7,
            "loss": 7,
            "rating": 8,
            "ratings": 8,
            "target price": 10,
            "analyst": 8,
            "brokerage": 8,
            "investment": 8,
            "investor": 8,
            "investors": 8,
            "ipo": 10,
            "acquisition": 7,
            "merger": 7,
            "debt": 6,
            "bonds": 6,
            "dividend": 8,
            "guidance": 7,
            "outlook": 7,
            "valuation": 8,
            "upgrade": 7,
            "downgrade": 7,
        }

        for keyword, points in financial_keywords.items():
            if keyword in text:
                score += points

        return score

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

        except (ValueError, TypeError):
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

    async def _ensure_sentiment(
        self,
        articles: list[NewsArticle],
    ) -> list[NewsArticle]:

        if not articles:
            return []

        articles_without_sentiment = [
            article
            for article in articles
            if not article.sentiment
        ]

        if not articles_without_sentiment:
            return articles

        sentiments = (
            await self.sentiment_service.analyze(
                articles_without_sentiment
            )
        )

        sentiment_by_title = {
            item["title"]: item["sentiment"]
            for item in sentiments
        }

        enriched_articles: list[NewsArticle] = []

        for article in articles:

            sentiment = (
                article.sentiment
                or sentiment_by_title.get(
                    article.title,
                    "neutral",
                )
            )

            enriched_articles.append(
                NewsArticle(
                    title=article.title,
                    summary=article.summary,
                    source=article.source,
                    published_at=article.published_at,
                    url=article.url,
                    sentiment=sentiment,
                )
            )

        return enriched_articles