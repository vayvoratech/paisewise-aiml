from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NewsArticle:
    title: str
    summary: str
    source: str
    published_at: str
    url: str
    sentiment: str | None = None


class NewsProvider(ABC):
    """
    Interface for retrieving financial news articles.
    """

    @abstractmethod
    def get_news(
        self,
        symbol: str,
        limit: int = 10,
    ) -> list[NewsArticle]:
        """
        Retrieve recent news articles for a symbol.
        """
        raise NotImplementedError