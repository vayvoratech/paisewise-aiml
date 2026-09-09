from datetime import date

import yfinance as yf

from app.services.benchmark_models import (
    BenchmarkPerformance,
)
from app.services.market_data_provider import (
    MarketDataProvider,
)


class NSEMarketDataProvider(MarketDataProvider):
    """
    Market data provider backed by Yahoo Finance.

    Yahoo Finance provides historical market data for
    NSE indices. The provider remains behind the
    MarketDataProvider abstraction so the data source
    can be replaced later without changing the
    comparison service.
    """

    INDEX_SYMBOLS = {
        "NIFTY 50": "^NSEI",
        "NIFTY 100": "^CNX100",
        "NIFTY 500": "^CRSLDX",
        "NIFTY BANK": "^NSEBANK",
        "NIFTY IT": "^CNXIT",
        "NIFTY AUTO": "^CNXAUTO",
        "NIFTY PHARMA": "^CNXPHARMA",
        "NIFTY FMCG": "^CNXFMCG",
        "NIFTY METAL": "^CNXMETAL",
        "NIFTY REALTY": "^CNXREALTY",
    }

    def get_performance(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> BenchmarkPerformance:

        if not symbol or not symbol.strip():
            raise ValueError(
                "symbol cannot be empty"
            )

        if start_date >= end_date:
            raise ValueError(
                "start_date must be before end_date"
            )

        index_name = symbol.strip().upper()

        ticker = self.INDEX_SYMBOLS.get(index_name)

        if ticker is None:
            raise ValueError(
                f"Unsupported benchmark index: "
                f"{index_name}"
            )

        try:
            data = yf.download(
                ticker,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                progress=False,
                auto_adjust=False,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Unable to retrieve market data "
                f"for {index_name}."
            ) from exc

        if data is None or data.empty:
            raise RuntimeError(
                f"No market data available for "
                f"{index_name}."
            )

        try:
            close_data = data["Close"]

            if hasattr(
                close_data,
                "columns",
            ):
                close_data = close_data.iloc[:, 0]

            close_data = close_data.dropna()

            if len(close_data) < 2:
                raise RuntimeError(
                    f"Insufficient market data available "
                    f"for {index_name}."
                )

            start_value = float(
                close_data.iloc[0]
            )

            end_value = float(
                close_data.iloc[-1]
            )

        except Exception as exc:
            raise RuntimeError(
                f"Unable to process market data "
                f"for {index_name}."
            ) from exc

        if start_value <= 0:
            raise RuntimeError(
                f"Invalid starting index value "
                f"for {index_name}."
            )

        return_percentage = (
            (end_value - start_value)
            / start_value
            * 100
        )

        return BenchmarkPerformance(
            name=index_name,
            return_percentage=round(
                return_percentage,
                2,
            ),
        )