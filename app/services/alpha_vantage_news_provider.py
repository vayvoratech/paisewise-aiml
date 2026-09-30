import os
from typing import Any

import requests
from dotenv import load_dotenv

from app.services.news_provider import NewsArticle, NewsProvider


load_dotenv()


class AlphaVantageNewsProvider(NewsProvider):
    """
    News provider backed by Alpha Vantage.

    Alpha Vantage sentiment labels are normalized to:
        positive
        negative
        neutral
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self) -> None:
        self.api_key = os.getenv(
            "ALPHA_VANTAGE_API_KEY"
        )

        if not self.api_key:
            raise RuntimeError(
                "ALPHA_VANTAGE_API_KEY is not configured"
            )

    def get_news(
        self,
        symbol: str,
        limit: int = 10,
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

        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": normalized_symbol,
            "sort": "LATEST",
            "limit": limit,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=15,
            )

            response.raise_for_status()

            data: dict[str, Any] = response.json()

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Unable to retrieve news for "
                f"{normalized_symbol}."
            ) from exc

        if "Error Message" in data:
            raise RuntimeError(
                str(data["Error Message"])
            )

        if "Information" in data:
            raise RuntimeError(
                str(data["Information"])
            )

        if "Note" in data:
            raise RuntimeError(
                str(data["Note"])
            )

        feed = data.get("feed", [])

        if not isinstance(feed, list):
            raise RuntimeError(
                "Invalid news response from "
                "Alpha Vantage."
            )

        articles: list[NewsArticle] = []

        for item in feed:

            if not isinstance(item, dict):
                continue

            title = str(
                item.get("title", "")
            ).strip()

            if not title:
                continue

            summary = str(
                item.get("summary", "")
            ).strip()

            source = str(
                item.get("source", "")
            ).strip()

            published_at = str(
                item.get("time_published", "")
            ).strip()

            url = str(
                item.get("url", "")
            ).strip()

            sentiment = self._get_sentiment(
                item
            )

            articles.append(
                NewsArticle(
                    title=title,
                    summary=summary,
                    source=source,
                    published_at=published_at,
                    url=url,
                    sentiment=sentiment,
                )
            )

            if len(articles) >= limit:
                break

        return articles

    @classmethod
    def _get_sentiment(
        cls,
        item: dict[str, Any],
    ) -> str | None:

        ticker_sentiment = item.get(
            "ticker_sentiment",
            [],
        )

        if isinstance(
            ticker_sentiment,
            list,
        ):

            for ticker in ticker_sentiment:

                if not isinstance(
                    ticker,
                    dict,
                ):
                    continue

                label = ticker.get(
                    "ticker_sentiment_label"
                )

                if label:
                    return cls._normalize_sentiment(
                        str(label)
                    )

        overall_label = item.get(
            "overall_sentiment_label"
        )

        if overall_label:
            return cls._normalize_sentiment(
                str(overall_label)
            )

        return None

    @staticmethod
    def _normalize_sentiment(
        sentiment: str,
    ) -> str:

        normalized = (
            sentiment.strip().lower()
        )

        if "bullish" in normalized:
            return "positive"

        if "bearish" in normalized:
            return "negative"

        if "neutral" in normalized:
            return "neutral"

        return "neutral"