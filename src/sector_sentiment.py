# PaiseWise Sector Sentiment

from sentiment_analyser import analyze_sentiment


def calculate_sector_sentiment(articles):

    sector_data = {}

    for article in articles:

        if not isinstance(article, dict):
            continue

        sector = article.get("sector")

        if not sector:
            continue

        title = article.get("title") or ""
        description = article.get("description") or ""

        text = title + ". " + description

        sentiment_result = analyze_sentiment(text)

        score = sentiment_result["score"]
        sentiment = sentiment_result["sentiment"]

        if sector not in sector_data:

            sector_data[sector] = {
                "scores": [],
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }

        sector_data[sector]["scores"].append(score)

        if sentiment == "Positive":

            sector_data[sector]["positive"] += 1

        elif sentiment == "Negative":

            sector_data[sector]["negative"] += 1

        else:

            sector_data[sector]["neutral"] += 1

    # Final sector sentiment

    result = {}

    for sector, data in sector_data.items():

        if not data["scores"]:
            continue

        average_score = (
            sum(data["scores"]) /
            len(data["scores"])
        )

        if average_score >= 0.05:

            overall_sentiment = "Positive"

        elif average_score <= -0.05:

            overall_sentiment = "Negative"

        else:

            overall_sentiment = "Neutral"

        result[sector] = {

            "sentiment": overall_sentiment,

            "score": round(
                average_score,
                4
            ),

            "article_count": len(
                data["scores"]
            )
        }

    return result