from collections import defaultdict

from sentiment_analyser import analyze_sentiment


# Calculate sentiment for each sector
def calculate_sector_sentiment(articles):

    sector_scores = defaultdict(list)

    for article in articles:

        text = article["title"]

        sentiment, score = analyze_sentiment(text)

        sector = article["sector"]

        sector_scores[sector].append(score)

    sector_results = {}

    for sector, scores in sector_scores.items():

        average_score = sum(scores) / len(scores)

        if average_score >= 0.05:
            overall_sentiment = "Positive"

        elif average_score <= -0.05:
            overall_sentiment = "Negative"

        else:
            overall_sentiment = "Neutral"

        sector_results[sector] = {
            "sentiment": overall_sentiment,
            "score": round(average_score, 4),
            "article_count": len(scores)
        }

    return sector_results


# Test the sector sentiment calculation
if __name__ == "__main__":

    print("=" * 60)
    print("PaiseWise Sector Sentiment")
    print("=" * 60)

    articles = [

        {
            "title": "TCS reports strong growth and excellent profits",
            "sector": "IT"
        },

        {
            "title": "IT company wins a major technology contract",
            "sector": "IT"
        },

        {
            "title": "Bank shares fall after weak financial results",
            "sector": "Banking"
        },

        {
            "title": "Bank reports strong quarterly performance",
            "sector": "Banking"
        },

        {
            "title": "Pharma company receives regulatory approval",
            "sector": "Pharma"
        }
    ]

    results = calculate_sector_sentiment(articles)

    print("\nSector Sentiment Results:")

    for sector, result in results.items():

        print()
        print("Sector:", sector)
        print("Sentiment:", result["sentiment"])
        print("Average Score:", result["score"])
        print("Articles:", result["article_count"])

    print()
    print("Sector sentiment calculation completed successfully.")