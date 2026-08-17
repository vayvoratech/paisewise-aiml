import requests

from app.config.settings import NEWS_API_KEY


def get_news():
    if not NEWS_API_KEY:
        raise RuntimeError("NEWS_API_KEY is not set.")

    response = requests.get(
        "https://newsapi.org/v2/top-headlines",
        params={
            "category": "business",
            "country": "in",
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
