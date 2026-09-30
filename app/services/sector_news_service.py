from datetime import datetime, timedelta, timezone

from app.services.google_news_provider import GoogleNewsProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.news_provider import NewsArticle
from app.services.news_sentiment_service import NewsSentimentService


class SectorNewsService:
    """
    Retrieves recent news for a sector dynamically.

    Uses Google News for article retrieval and the existing
    LLM sentiment service when provider sentiment is unavailable.
    """

    RECENT_NEWS_DAYS = 2

    def __init__(
        self,
        google_provider: GoogleNewsProvider | None = None,
        sentiment_service: NewsSentimentService | None = None,
    ) -> None:
        self.google_provider = (
            google_provider or GoogleNewsProvider()
        )

        self.sentiment_service = (
            sentiment_service
            or NewsSentimentService(
                llm_provider=GeminiProvider()
            )
        )

    async def get_news(
        self,
        sector: str,
        limit: int = 5,
    ) -> list[NewsArticle]:

        if not sector or not sector.strip():
            raise ValueError("sector cannot be empty")

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

        normalized_sector = sector.strip()

        try:
            articles = self.google_provider.get_news(
                symbol=normalized_sector,
                company_name=normalized_sector,
                limit=max(limit * 3, 10),
            )
        except RuntimeError as exc:
            raise RuntimeError(
                f"Unable to retrieve news for sector "
                f"{normalized_sector}."
            ) from exc

        selected = self._select_recent_articles(
            articles,
            limit,
        )

        return await self._ensure_sentiment(selected)

    def get_latest_article_metadata(
        self,
        sector: str,
    ) -> tuple[str | None, str | None]:
        """
        Return metadata for the latest available source article.

        This method is intentionally lightweight.
        It does not run sentiment analysis.

        It is used only to determine whether the cached
        processed sector news needs to be refreshed.
        """

        if not sector or not sector.strip():
            raise ValueError(
                "sector cannot be empty"
            )

        normalized_sector = sector.strip()

        try:
            articles = self.google_provider.get_news(
                symbol=normalized_sector,
                company_name=normalized_sector,
                limit=10,
            )
        except RuntimeError as exc:
            raise RuntimeError(
                f"Unable to check latest news for sector "
                f"{normalized_sector}."
            ) from exc

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

    def _select_recent_articles(
        self,
        articles: list[NewsArticle],
        limit: int,
    ) -> list[NewsArticle]:

        if not articles:
            return []

        cutoff = (
            datetime.now(timezone.utc)
            - timedelta(days=self.RECENT_NEWS_DAYS)
        )

        recent = []

        for article in articles:
            published = self._parse_datetime(
                article.published_at
            )

            if published is None:
                continue

            if published >= cutoff:
                recent.append(article)

        recent.sort(
            key=lambda article: self._publication_timestamp(
                article.published_at
            ),
            reverse=True,
        )

        return recent[:limit]

    @staticmethod
    def _parse_datetime(
        value: str,
    ) -> datetime | None:

        if not value:
            return None

        try:
            parsed = datetime.fromisoformat(
                value.replace("Z", "+00:00")
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

        without_sentiment = [
            article
            for article in articles
            if not article.sentiment
        ]

        if not without_sentiment:
            return articles

        sentiments = await self.sentiment_service.analyze(
            without_sentiment
        )

        sentiment_by_title = {
            item["title"]: item["sentiment"]
            for item in sentiments
        }

        enriched = []

        for article in articles:
            sentiment = (
                article.sentiment
                or sentiment_by_title.get(
                    article.title,
                    "neutral",
                )
            )

            enriched.append(
                NewsArticle(
                    title=article.title,
                    summary=article.summary,
                    source=article.source,
                    published_at=article.published_at,
                    url=article.url,
                    sentiment=sentiment,
                )
            )

        return enriched