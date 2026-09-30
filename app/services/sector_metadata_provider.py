from dataclasses import dataclass

import yfinance as yf


@dataclass(frozen=True)
class StockSector:
    symbol: str
    company_name: str
    sector: str


class SectorMetadataProvider:
    """
    Dynamically resolves stock sector information.

    This provider does not access the user portfolio database.
    """

    SYMBOL_SUFFIX = ".NS"

    def get_sector(self, symbol: str) -> StockSector | None:
        if not symbol or not symbol.strip():
            raise ValueError("symbol cannot be empty")

        normalized_symbol = symbol.strip().upper()

        yahoo_symbol = self._to_yahoo_symbol(normalized_symbol)

        try:
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
        except Exception:
            return None

        sector = str(info.get("sector") or "").strip()
        company_name = str(
            info.get("longName")
            or info.get("shortName")
            or normalized_symbol
        ).strip()

        if not sector:
            return None

        return StockSector(
            symbol=normalized_symbol,
            company_name=company_name,
            sector=sector,
        )

    @classmethod
    def _to_yahoo_symbol(cls, symbol: str) -> str:
        """
        Converts application symbols such as NSE:RELIANCE
        into Yahoo Finance symbols such as RELIANCE.NS.
        """

        if ":" in symbol:
            exchange, ticker = symbol.split(":", 1)

            exchange = exchange.upper().strip()
            ticker = ticker.upper().strip()

            if exchange == "NSE":
                return f"{ticker}{cls.SYMBOL_SUFFIX}"

            if exchange == "BSE":
                return ticker

            return ticker

        if symbol.startswith("^"):
            return symbol

        return f"{symbol}{cls.SYMBOL_SUFFIX}"