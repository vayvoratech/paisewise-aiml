import requests

from app.config.settings import NEWS_API_KEY


def get_news():
    if not NEWS_API_KEY:
        raise RuntimeError("NEWS_API_KEY is not set.")

    # NOTE: NewsAPI's /top-headlines with country=in reliably returns
    # zero results on the free tier (a known issue on their side, not
    # our key). /everything with a search query is more reliable, so
    # we use that instead and sort by most recent.
    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": "India business OR Indian stock market OR NSE OR BSE",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 3,
            "apiKey": NEWS_API_KEY,
        },
        timeout=20,
    )
    response.raise_for_status()

    articles = response.json().get("articles", [])

    return [
        {
            "title": item.get("title"),
            "source": item.get("source", {}).get("name"),
        }
        for item in articles[:3]
    ]
