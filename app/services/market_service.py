import os

import requests

from app.config.settings import ALPHA_VANTAGE_API_KEY


ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"


def _get_quote(symbol):
    if not ALPHA_VANTAGE_API_KEY:
        raise RuntimeError("ALPHA_VANTAGE_API_KEY is not set.")

    response = requests.get(
        ALPHA_VANTAGE_URL,
        params={
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("Global Quote", {})


def get_market(symbol):
    quote = _get_quote(symbol)

    if not quote:
        return None

    return {
        "symbol": quote.get("01. symbol"),
        "open": quote.get("02. open"),
        "high": quote.get("03. high"),
        "low": quote.get("04. low"),
        "price": quote.get("05. price"),
        "previous_close": quote.get("08. previous close"),
        "change_percent": quote.get("10. change percent"),
    }


def get_configured_market_movements(limit=5):
    """Fetch the configured NSE/index symbols and return the largest moves."""
    symbols = [
        value.strip()
        for value in os.getenv("MARKET_SYMBOLS", "").split(",")
        if value.strip()
    ]

    movements = []
    for symbol in symbols:
        quote = get_market(symbol)
        if quote and quote.get("change_percent") is not None:
            movements.append(quote)

    def change_value(item):
        value = str(item.get("change_percent", "0")).replace("%", "")
        try:
            return abs(float(value))
        except ValueError:
            return 0

    return sorted(movements, key=change_value, reverse=True)[:limit]


def get_sector_performance():
    """Fetch sector performance from Alpha Vantage's sector endpoint."""
    if not ALPHA_VANTAGE_API_KEY:
        raise RuntimeError("ALPHA_VANTAGE_API_KEY is not set.")

    response = requests.get(
        ALPHA_VANTAGE_URL,
        params={
            "function": "SECTOR",
            "apikey": ALPHA_VANTAGE_API_KEY,
        },
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    performance = []
    for name, value in data.items():
        if "real-time performance" not in name.lower():
            continue
        if not isinstance(value, dict):
            continue
        for sector, change in value.items():
            performance.append(
                {
                    "sector": sector,
                    "change_percent": change,
                }
            )

    return performance
