from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Create sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


# Analyze the sentiment of a news article
def analyze_sentiment(text):

    result = analyzer.polarity_scores(text)

    score = result["compound"]

    if score >= 0.05:
        sentiment = "Positive"

    elif score <= -0.05:
        sentiment = "Negative"

    else:
        sentiment = "Neutral"

    return sentiment, score


# Test the sentiment analyzer
if __name__ == "__main__":

    print("=" * 60)
    print("PaiseWise News Sentiment Analyzer")
    print("=" * 60)

    articles = [
        "TCS reports strong quarterly growth and excellent profits.",
        "Bank shares fall sharply after weak financial results.",
        "The company announced its quarterly results today."
    ]

    for number, article in enumerate(articles, start=1):

        sentiment, score = analyze_sentiment(article)

        print()
        print("Article", number)
        print("News:", article)
        print("Sentiment:", sentiment)
        print("Score:", round(score, 4))

    print()
    print("Sentiment analysis completed successfully.")