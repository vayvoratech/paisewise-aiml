from datetime import datetime, timezone
from html import unescape
from xml.etree import ElementTree
import re

import requests

from app.services.news_provider import NewsArticle, NewsProvider


class GoogleNewsProvider(NewsProvider):
    """
    News provider using Google News RSS search.

    The company name is supplied dynamically by the caller.
    No hardcoded company-name mapping is maintained here.
    """

    BASE_URL = "https://news.google.com/rss/search"

    def get_news(
        self,
        symbol: str,
        limit: int = 10,
        company_name: str | None = None,
    ) -> list[NewsArticle]:

        if not symbol or not symbol.strip():
            raise ValueError(
                "symbol cannot be empty"
            )

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

        normalized_symbol = symbol.strip().upper()

        search_name = (
            company_name.strip()
            if company_name
            and company_name.strip()
            else normalized_symbol
        )

        query = f'"{search_name}"'

        params = {
            "q": query,
            "hl": "en-IN",
            "gl": "IN",
            "ceid": "IN:en",
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=15,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "PaiseWise/1.0"
                    )
                },
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Unable to retrieve news for "
                f"{normalized_symbol}."
            ) from exc

        try:
            root = ElementTree.fromstring(
                response.content
            )

        except ElementTree.ParseError as exc:
            raise RuntimeError(
                "Invalid RSS response from Google News."
            ) from exc

        articles: list[NewsArticle] = []

        for item in root.findall(".//item"):

            title = self._get_text(
                item,
                "title",
            )

            link = self._get_text(
                item,
                "link",
            )

            description = self._get_text(
                item,
                "description",
            )

            published_at = self._get_text(
                item,
                "pubDate",
            )

            source_element = item.find(
                "source"
            )

            source = ""

            if source_element is not None:
                source = (
                    source_element.text or ""
                ).strip()

            if not title:
                continue

            articles.append(
                NewsArticle(
                    title=title,
                    summary=self._clean_summary(
                        description
                    ),
                    source=source,
                    published_at=self._normalize_date(
                        published_at
                    ),
                    url=link,
                    sentiment=None,
                )
            )

            if len(articles) >= limit:
                break

        return articles

    @staticmethod
    def _get_text(
        item: ElementTree.Element,
        tag: str,
    ) -> str:

        element = item.find(tag)

        if element is None:
            return ""

        return (
            element.text or ""
        ).strip()

    @staticmethod
    def _clean_summary(
        value: str,
    ) -> str:

        if not value:
            return ""

        text = unescape(value)

        text = re.sub(
            r"<[^>]+>",
            " ",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @staticmethod
    def _normalize_date(
        value: str,
    ) -> str:

        if not value:
            return ""

        try:
            parsed = datetime.strptime(
                value,
                "%a, %d %b %Y %H:%M:%S %Z",
            )

            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

            return parsed.isoformat()

        except ValueError:
            return value