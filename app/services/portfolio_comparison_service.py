from datetime import date

from app.schemas.portfolio_comparison import (
    BenchmarkComparison,
    PortfolioComparisonResponse,
)
from app.services.benchmark_service import BenchmarkService
from app.services.portfolio_analytics_service import (
    PortfolioAnalyticsService,
)


class PortfolioComparisonService:
    """
    Compares the user's portfolio performance with
    externally provided benchmark performance.

    Portfolio analytics come from the existing
    PortfolioAnalyticsService.

    Benchmark data comes from BenchmarkService,
    which delegates market-data retrieval to a
    configured MarketDataProvider.
    """

    def __init__(
        self,
        portfolio_analytics_service: (
            PortfolioAnalyticsService | None
        ) = None,
        benchmark_service: BenchmarkService | None = None,
    ) -> None:
        self.portfolio_analytics_service = (
            portfolio_analytics_service
            or PortfolioAnalyticsService()
        )
        self.benchmark_service = (
            benchmark_service
            or BenchmarkService()
        )

    def compare(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        sectors: list[str] | None = None,
    ) -> PortfolioComparisonResponse:
        """
        Compare portfolio performance against NIFTY 50
        and optionally supplied sector indices.
        """

        if not user_id or not user_id.strip():
            raise ValueError(
                "user_id cannot be empty"
            )

        if start_date >= end_date:
            raise ValueError(
                "start_date must be before end_date"
            )

        analytics = (
            self.portfolio_analytics_service.calculate(
                user_id=user_id.strip()
            )
        )

        total_invested = float(
            analytics.totalInvested
        )
        total_pnl = float(
            analytics.totalPnl
        )

        if total_invested > 0:
            portfolio_return = (
                total_pnl
                / total_invested
                * 100
            )
        else:
            portfolio_return = 0.0

        benchmarks: list[BenchmarkComparison] = []

        nifty = (
            self.benchmark_service
            .get_nifty_50_performance(
                start_date=start_date,
                end_date=end_date,
            )
        )

        benchmarks.append(
            BenchmarkComparison(
                name=nifty.name,
                returnPercentage=round(
                    nifty.return_percentage,
                    2,
                ),
                differenceFromPortfolio=round(
                    portfolio_return
                    - nifty.return_percentage,
                    2,
                ),
            )
        )

        for sector in sectors or []:
            benchmark = (
                self.benchmark_service
                .get_sector_performance(
                    sector=sector,
                    start_date=start_date,
                    end_date=end_date,
                )
            )

            benchmarks.append(
                BenchmarkComparison(
                    name=benchmark.name,
                    returnPercentage=round(
                        benchmark.return_percentage,
                        2,
                    ),
                    differenceFromPortfolio=round(
                        portfolio_return
                        - benchmark.return_percentage,
                        2,
                    ),
                )
            )

        return PortfolioComparisonResponse(
            userId=user_id.strip(),
            startDate=start_date.isoformat(),
            endDate=end_date.isoformat(),
            portfolioReturnPercentage=round(
                portfolio_return,
                2,
            ),
            benchmarks=benchmarks,
        )