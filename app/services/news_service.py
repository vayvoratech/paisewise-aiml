import time
import requests
from app.config.settings import NEWS_API_KEY

_CACHE: dict[str, tuple[float, list[dict]]] = {}
CACHE_SECONDS = 2 * 60 * 60


def get_news(limit: int = 20):
    cached = _CACHE.get("india_market")
    if cached and time.time() - cached[0] < CACHE_SECONDS:
        return cached[1][:limit]

    if not NEWS_API_KEY:
        return []

    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": "India business OR Indian stock market OR NSE OR BSE",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(limit, 100),
            "apiKey": NEWS_API_KEY,
        },
        timeout=20,
    )
    response.raise_for_status()
    articles = response.json().get("articles", [])
    result = [
        {
            "title": item.get("title"),
            "description": item.get("description"),
            "source": item.get("source", {}).get("name"),
            "published_at": item.get("publishedAt"),
            "url": item.get("url"),
        }
        for item in articles[:20]
    ]
    _CACHE["india_market"] = (time.time(), result)
    return result[:limit]
