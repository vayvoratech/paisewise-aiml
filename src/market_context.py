
from datetime import datetime


def create_market_context(
    news_count,
    sector_sentiment,
    nifty_change,
    corporate_events
):

    current_time = datetime.now()

    current_date = current_time.strftime(
        "%Y-%m-%d"
    )

    updated_at = current_time.isoformat(
        timespec="seconds"
    )

    market_direction = "Stable"

    if nifty_change > 0:
        market_direction = "Positive"

    elif nifty_change < 0:
        market_direction = "Negative"

    context = {

        "date": current_date,

        "updated_at": updated_at,

        "market": {

            "index": "NIFTY 50",

            "change_percent": round(
                nifty_change,
                2
            ),

            "direction": market_direction
        },

        "news": {

            "articles_analyzed": news_count
        },

        "sector_sentiment": sector_sentiment,

        "major_corporate_events": corporate_events
    }

    return context


if __name__ == "__main__":

    print("=" * 60)
    print("PaiseWise Market Context")
    print("=" * 60)

    sector_sentiment = {

        "IT": {

            "sentiment": "Positive",

            "score": 0.42,

            "article_count": 5
        },

        "Banking": {

            "sentiment": "Neutral",

            "score": 0.01,

            "article_count": 6
        },

        "Pharma": {

            "sentiment": "Positive",

            "score": 0.35,

            "article_count": 3
        }
    }

    corporate_events = [

        {

            "title":
                "TCS reports quarterly results",

            "event_type":
                "Quarterly Results",

            "source":
                "Example Source"
        },

        {

            "title":
                "Sun Pharma receives regulatory approval",

            "event_type":
                "Regulatory Approval",

            "source":
                "Example Source"
        }
    ]

    context = create_market_context(

        news_count=20,

        sector_sentiment=sector_sentiment,

        nifty_change=0.75,

        corporate_events=corporate_events
    )

    print()

    print("Market Context:")

    print(context)

    print()

    print(
        "Market context created successfully."
    )