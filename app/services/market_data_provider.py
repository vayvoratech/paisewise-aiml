from abc import ABC, abstractmethod
from datetime import date

from app.services.benchmark_models import (
    BenchmarkPerformance,
)


class MarketDataProvider(ABC):
    """
    Interface for retrieving market and benchmark
    performance data.
    """

    @abstractmethod
    def get_performance(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> BenchmarkPerformance:
        raise NotImplementedError