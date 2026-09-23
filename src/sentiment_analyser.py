# PaiseWise Sentiment Analysis

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text):

    scores = analyzer.polarity_scores(text)

    compound_score = scores["compound"]

    if compound_score >= 0.05:

        sentiment = "Positive"

    elif compound_score <= -0.05:

        sentiment = "Negative"

    else:

        sentiment = "Neutral"

    return {

        "sentiment": sentiment,

        "score": round(
            compound_score,
            4
        )
    }