import yfinance as yf

from app.services.news_provider import NewsArticle, NewsProvider


class YFinanceNewsProvider(NewsProvider):
    """
    News provider backed by Yahoo Finance through yfinance.
    """

    SYMBOL_SUFFIX = ".NS"

    def get_news(
        self,
        symbol: str,
        limit: int = 10,
    ) -> list[NewsArticle]:

        if not symbol or not symbol.strip():
            raise ValueError("symbol cannot be empty")

        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        normalized_symbol = symbol.strip().upper()

        ticker_symbol = self._to_yahoo_symbol(
            normalized_symbol
        )

        try:
            ticker = yf.Ticker(ticker_symbol)
            raw_news = ticker.news
        except Exception as exc:
            raise RuntimeError(
                f"Unable to retrieve news for {normalized_symbol}."
            ) from exc

        if not raw_news:
            return []

        articles: list[NewsArticle] = []

        for item in raw_news:
            content = item.get("content", item)

            title = content.get("title", "")
            summary = (
                content.get("summary")
                or content.get("description")
                or ""
            )

            provider = content.get("provider") or {}
            source = provider.get("displayName", "")

            canonical_url = content.get("canonicalUrl") or {}
            click_url = content.get("clickThroughUrl") or {}

            url = (
                canonical_url.get("url")
                or click_url.get("url")
                or ""
            )

            published_at = (
                content.get("pubDate")
                or content.get("displayTime")
                or ""
            )

            if not title:
                continue

            articles.append(
                NewsArticle(
                    title=str(title),
                    summary=str(summary),
                    source=str(source),
                    published_at=str(published_at),
                    url=str(url),
                )
            )

            if len(articles) >= limit:
                break

        return articles

    def _to_yahoo_symbol(self, symbol: str) -> str:
        """
        Convert an application symbol into a Yahoo Finance ticker.

        Examples:
            RELIANCE -> RELIANCE.NS
            INFY -> INFY.NS
            ^NSEI -> ^NSEI
            RELIANCE.NS -> RELIANCE.NS
        """

        if symbol.startswith("^"):
            return symbol

        if symbol.endswith(self.SYMBOL_SUFFIX):
            return symbol

        return f"{symbol}{self.SYMBOL_SUFFIX}"