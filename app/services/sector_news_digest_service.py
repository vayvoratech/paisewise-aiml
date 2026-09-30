import json

from app.services.llm.base import LLMProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.sector_news_service import SectorNewsService


class SectorNewsDigestService:
    """
    Generates a daily bilingual sector-news digest.

    Sector names and news articles are supplied dynamically.
    No stock or sector mapping is hardcoded here.
    """

    def __init__(
        self,
        sector_news_service: SectorNewsService | None = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self.sector_news_service = (
            sector_news_service
            or SectorNewsService()
        )

        self.llm_provider = (
            llm_provider
            or GeminiProvider()
        )

    async def generate(
        self,
        sectors: list[str],
    ) -> dict[str, dict]:

        if not sectors:
            return {}

        digest: dict[str, dict] = {}

        unique_sectors = {
            sector.strip()
            for sector in sectors
            if sector and sector.strip()
        }

        for sector in sorted(unique_sectors):

            articles = (
                await self.sector_news_service.get_news(
                    sector=sector,
                    limit=5,
                )
            )

            article_data = [
                {
                    "title": article.title,
                    "summary": article.summary,
                    "source": article.source,
                    "publishedAt": article.published_at,
                    "sentiment": (
                        article.sentiment
                        or "neutral"
                    ),
                }
                for article in articles
            ]

            english_digest, hindi_digest = (
                await self._generate_bilingual_digest(
                    sector=sector,
                    articles=article_data,
                )
            )

            digest[sector] = {
                "englishDigest": english_digest,
                "hindiDigest": hindi_digest,
                "articles": article_data,
            }

        return digest

    async def _generate_bilingual_digest(
        self,
        sector: str,
        articles: list[dict],
    ) -> tuple[str, str]:

        articles_json = json.dumps(
            articles,
            ensure_ascii=False,
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a financial news summarizer. "
                    "Use only the supplied news articles. "
                    "Do not invent or assume facts. "
                    "Create two concise summaries of the supplied "
                    "news: one in plain English and one in plain Hindi. "
                    "The summaries must be understandable to a retail "
                    "investor and must reflect only the provided news. "
                    "If no articles are supplied, clearly state that "
                    "there is no recent news available. "
                    "Return ONLY valid JSON with exactly these fields: "
                    "englishDigest and hindiDigest."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Sector: {sector}\n"
                    f"News articles:\n{articles_json}"
                ),
            },
        ]

        response = await self.llm_provider.generate(
            messages
        )

        try:
            parsed = json.loads(response)

            english_digest = str(
                parsed["englishDigest"]
            ).strip()

            hindi_digest = str(
                parsed["hindiDigest"]
            ).strip()

            return (
                english_digest,
                hindi_digest,
            )

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            AttributeError,
        ) as exc:
            raise RuntimeError(
                "LLM returned an invalid bilingual sector digest."
            ) from exc