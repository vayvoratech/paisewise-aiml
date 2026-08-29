# PaiseWise Market Context


def create_market_context(
    news_count,
    sector_sentiment,
    nifty_change
):

    market_direction = "Stable"

    if nifty_change > 0:
        market_direction = "Positive"

    elif nifty_change < 0:
        market_direction = "Negative"

    context = {
        "market": {
            "index": "NIFTY 50",
            "change_percent": round(nifty_change, 2),
            "direction": market_direction
        },

        "news": {
            "articles_analyzed": news_count
        },

        "sector_sentiment": sector_sentiment
    }

    return context


# Test the market context
if __name__ == "__main__":

    print("=" * 60)
    print("PaiseWise Market Context")
    print("=" * 60)

    sector_sentiment = {
        "IT": {
            "sentiment": "Positive",
            "score": 0.42
        },

        "Banking": {
            "sentiment": "Neutral",
            "score": 0.01
        },

        "Pharma": {
            "sentiment": "Positive",
            "score": 0.35
        }
    }

    context = create_market_context(
        news_count=20,
        sector_sentiment=sector_sentiment,
        nifty_change=0.75
    )

    print()
    print(context)

    print()
    print("Market context created successfully.")