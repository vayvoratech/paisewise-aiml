# PaiseWise News Ingestion

import os
import requests


NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def fetch_market_news():

    if not NEWS_API_KEY:

        raise ValueError(
            "NEWS_API_KEY environment variable is not set."
        )

    url = "https://newsapi.org/v2/everything"

    params = {

        "q": "NSE OR BSE OR NIFTY OR Sensex",

        "language": "en",

        "sortBy": "publishedAt",

        "pageSize": 20,

        "apiKey": NEWS_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    articles = data.get(
        "articles",
        []
    )

    news = []

    for article in articles:

        news.append({

            "title": article.get("title"),

            "description": article.get(
                "description"
            ),

            "source": article.get(
                "source",
                {}
            ).get("name"),

            "published_at": article.get(
                "publishedAt"
            ),

            "url": article.get("url")
        })

    return news


if __name__ == "__main__":

    print("=" * 60)
    print("PaiseWise News Ingestion")
    print("=" * 60)

    articles = fetch_market_news()

    print(
        "Articles fetched:",
        len(articles)
    )

    print()

    for number, article in enumerate(
        articles,
        start=1
    ):

        print(
            f"{number}. {article['title']}"
        )

    print()

    print(
        "News ingestion completed successfully."
    )