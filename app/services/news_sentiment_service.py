import json

from app.services.llm.base import LLMProvider
from app.services.news_provider import NewsArticle


class NewsSentimentService:
    """
    Uses an LLM to classify financial-news sentiment.
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    async def analyze(
        self,
        articles: list[NewsArticle],
    ) -> list[dict]:

        if not articles:
            return []

        articles_text = "\n\n".join(
            (
                f"TITLE: {article.title}\n"
                f"SUMMARY: {article.summary}\n"
                f"SOURCE: {article.source}"
            )
            for article in articles
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a financial news sentiment classifier. "
                    "Analyze only the provided articles. "
                    "For each article, classify sentiment as exactly "
                    "one of: positive, negative, neutral. "
                    "Return ONLY valid JSON as an array. "
                    "Each item must contain: title and sentiment."
                ),
            },
            {
                "role": "user",
                "content": articles_text,
            },
        ]

        response = await self.llm_provider.generate(messages)

        return self._parse_response(response, articles)

    @staticmethod
    def _parse_response(
        response: str,
        articles: list[NewsArticle],
    ) -> list[dict]:

        text = response.strip()

        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        try:
            result = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "LLM returned invalid sentiment JSON."
            ) from exc

        if not isinstance(result, list):
            raise RuntimeError(
                "LLM sentiment response must be a JSON array."
            )

        valid_sentiments = {
            "positive",
            "negative",
            "neutral",
        }

        output = []

        for item in result:
            if not isinstance(item, dict):
                continue

            title = str(item.get("title", "")).strip()
            sentiment = str(
                item.get("sentiment", "")
            ).strip().lower()

            if not title:
                continue

            if sentiment not in valid_sentiments:
                raise RuntimeError(
                    f"Invalid sentiment value: {sentiment}"
                )

            output.append(
                {
                    "title": title,
                    "sentiment": sentiment,
                }
            )

        if not output:
            raise RuntimeError(
                "LLM returned no valid sentiment results."
            )

        return output