from collections import defaultdict
from typing import Any


class NewsContextService:
    SECTORS = {
        "IT": ["software", "technology", "IT", "infosys", "tcs", "wipro"],
        "Banking": ["bank", "banking", "HDFC", "ICICI", "SBI"],
        "Pharma": ["pharma", "drug", "healthcare", "medicine"],
        "Auto": ["auto", "automobile", "EV", "vehicle"],
        "FMCG": ["FMCG", "consumer", "food", "beverage"],
        "Metal": ["steel", "metal", "aluminium", "mining"],
    }

    def __init__(self):
        self.sentiment = None
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.sentiment = SentimentIntensityAnalyzer()
        except Exception:
            self.sentiment = None
        self.zero_shot = None
        try:
            from transformers import pipeline
            self.zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        except Exception:
            self.zero_shot = None

    def classify_sector(self, text: str) -> str:
        if self.zero_shot:
            labels = list(self.SECTORS) + ["Other"]
            result = self.zero_shot(text[:1000], candidate_labels=labels, multi_label=False)
            return result["labels"][0]
        text_lower = text.lower()
        scores = {sector: sum(1 for term in terms if term.lower() in text_lower) for sector, terms in self.SECTORS.items()}
        return max(scores, key=scores.get) if max(scores.values(), default=0) else "Other"

    def _sentiment_score(self, text: str) -> float:
        if self.sentiment:
            return float(self.sentiment.polarity_scores(text)["compound"])
        positive = {"gain", "growth", "positive", "profit", "rise", "strong"}
        negative = {"loss", "fall", "negative", "decline", "weak", "drop"}
        words = set(text.lower().split())
        return round((len(words & positive) - len(words & negative)) / max(len(words), 1), 4)

    def enrich(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        enriched = []
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            score = self._sentiment_score(text)
            label = "positive" if score > 0.05 else "negative" if score < -0.05 else "neutral"
            enriched.append({**article, "sector": self.classify_sector(text), "sentiment": score, "sentiment_label": label})
        return enriched

    def sector_digest(self, articles: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
        grouped = defaultdict(list)
        for article in articles:
            grouped[article.get("sector", "Other")].append(float(article.get("sentiment", 0.0)))
        return {sector: {"sentiment": round(sum(values) / len(values), 4), "article_count": len(values)} for sector, values in grouped.items()}
