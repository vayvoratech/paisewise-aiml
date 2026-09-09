from app.services.benchmark_models import (
    BenchmarkPerformance,
)
from app.services.market_data_provider import (
    MarketDataProvider,
)


class BenchmarkService:
    """
    Provides benchmark performance data for
    portfolio comparisons.

    The actual market-data provider can be connected
    without changing PortfolioComparisonService.
    """

    def __init__(
        self,
        market_data_provider: MarketDataProvider | None = None,
    ) -> None:
        self.market_data_provider = market_data_provider

    def get_nifty_50_performance(
        self,
        start_date,
        end_date,
    ) -> BenchmarkPerformance:
        if self.market_data_provider is None:
            raise RuntimeError(
                "NIFTY 50 market data provider "
                "is not configured"
            )

        return self.market_data_provider.get_performance(
            symbol="NIFTY 50",
            start_date=start_date,
            end_date=end_date,
        )

    def get_sector_performance(
        self,
        sector: str,
        start_date,
        end_date,
    ) -> BenchmarkPerformance:
        if not sector or not sector.strip():
            raise ValueError(
                "sector cannot be empty"
            )

        if self.market_data_provider is None:
            raise RuntimeError(
                "Sector market data provider "
                "is not configured"
            )

        return self.market_data_provider.get_performance(
            symbol=sector.strip(),
            start_date=start_date,
            end_date=end_date,
        )