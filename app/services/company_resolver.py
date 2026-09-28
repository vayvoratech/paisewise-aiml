import os
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


class CompanyResolver:
    """
    Dynamically resolves a stock symbol to a company name.

    Uses Alpha Vantage SYMBOL_SEARCH instead of maintaining
    a hardcoded symbol-to-company-name mapping.
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self) -> None:
        self.api_key = os.getenv(
            "ALPHA_VANTAGE_API_KEY"
        )

        if not self.api_key:
            raise RuntimeError(
                "ALPHA_VANTAGE_API_KEY is not configured"
            )

    def resolve(
        self,
        symbol: str,
    ) -> str:

        if not symbol or not symbol.strip():
            raise ValueError(
                "symbol cannot be empty"
            )

        normalized_symbol = (
            symbol.strip().upper()
        )

        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": normalized_symbol,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=15,
            )

            response.raise_for_status()
            data: dict[str, Any] = response.json()

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Unable to resolve company for "
                f"{normalized_symbol}."
            ) from exc

        if "Error Message" in data:
            raise RuntimeError(
                str(data["Error Message"])
            )

        if "Information" in data:
            raise RuntimeError(
                str(data["Information"])
            )

        matches = data.get(
            "bestMatches",
            [],
        )

        if not isinstance(matches, list):
            raise RuntimeError(
                "Invalid symbol search response."
            )

        # Prefer an Indian/Bombay listing when available.
        for match in matches:
            if not isinstance(match, dict):
                continue

            match_symbol = str(
                match.get("1. symbol", "")
            ).upper()

            region = str(
                match.get("4. region", "")
            ).lower()

            if (
                normalized_symbol
                in match_symbol
                and (
                    "india" in region
                    or "bombay" in region
                )
            ):
                name = str(
                    match.get("2. name", "")
                ).strip()

                if name:
                    return name

        # Otherwise use the closest symbol match.
        for match in matches:
            if not isinstance(match, dict):
                continue

            match_symbol = str(
                match.get("1. symbol", "")
            ).upper()

            if normalized_symbol == match_symbol:
                name = str(
                    match.get("2. name", "")
                ).strip()

                if name:
                    return name

        # Last fallback: search using the supplied symbol.
        return normalized_symbol