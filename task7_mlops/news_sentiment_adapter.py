from app.services.news_sentiment_service import NewsSentimentService
from app.services.llm.base import LLMProvider
from app.services.news_provider import NewsArticle


class NewsSentimentAdapter:
    """
    MLOps adapter for the existing News Sentiment component.

    The original news_sentiment_service.py is not modified.
    """

    model_name = "News Sentiment"
    model_version = "v1"
    model_type = "llm_based"

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.service = NewsSentimentService(llm_provider)

    async def predict(
        self,
        articles: list[NewsArticle],
    ) -> list[dict]:
        return await self.service.analyze(articles)

    def metadata(self) -> dict[str, str]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_type": self.model_type,
        }