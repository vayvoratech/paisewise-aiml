import requests

from app.config.settings import AI_SERVICE_URL


def call_ai(user_id, language, market_context=None, holdings=None):
    if not AI_SERVICE_URL:
        raise RuntimeError("AI_SERVICE_URL is not set.")

    payload = {
        "userId": str(user_id),
        "language": language,
        "marketContext": market_context or {},
        "holdings": holdings or [],
    }

    response = requests.post(
        AI_SERVICE_URL,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
