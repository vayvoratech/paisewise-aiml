from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# -----------------------------
# Sector Classification
# -----------------------------

SECTORS = [
    "IT",
    "Banking",
    "Pharma",
    "Auto",
    "FMCG",
    "Energy",
    "Telecom",
    "Real Estate",
    "Infrastructure",
    "Metals and Mining",
    "Financial Services",
    "Consumer Durables",
    "Others"
]

print("Loading news classifier...")

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

print("News classifier loaded!")


# -----------------------------
# Sentiment Analysis
# -----------------------------

analyzer = SentimentIntensityAnalyzer()


def analyse_news(title, content):

    text = f"{title}. {content}"

    # Sector classification
    classification = classifier(
        text,
        candidate_labels=SECTORS,
        multi_label=False
    )

    sector = classification["labels"][0]
    sector_confidence = classification["scores"][0]

    if sector_confidence < 0.60:
        sector = "Others"

    # Sentiment analysis
    sentiment_scores = analyzer.polarity_scores(text)
    compound = sentiment_scores["compound"]

    if compound >= 0.05:
        sentiment = "Positive"
    elif compound <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "sector": sector,
        "sector_confidence": round(sector_confidence, 4),
        "sentiment": sentiment,
        "sentiment_score": round(compound, 4)
    }


# -----------------------------
# Test
# -----------------------------

if __name__ == "__main__":

    title = "Tata Motors reports strong growth in electric vehicle sales"

    content = """
    Tata Motors reported strong growth in electric vehicle sales
    during the quarter. The company expects continued demand and
    positive growth in the electric vehicle market.
    """

    result = analyse_news(title, content)

    print("\nNews Analysis")
    print("-------------")
    print("Title:", title)
    print("Sector:", result["sector"])
    print("Sector Confidence:", result["sector_confidence"])
    print("Sentiment:", result["sentiment"])
    print("Sentiment Score:", result["sentiment_score"])