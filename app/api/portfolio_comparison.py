from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.portfolio_comparison import (
    PortfolioComparisonResponse,
)
from app.services.benchmark_service import (
    BenchmarkService,
)
from app.services.nse_market_data_provider import (
    NSEMarketDataProvider,
)
from app.services.portfolio_comparison_service import (
    PortfolioComparisonService,
)


router = APIRouter(
    prefix="/ai",
    tags=["Portfolio Comparison"],
)


@router.get(
    "/portfolio-analytics/comparison/{userId}",
    response_model=PortfolioComparisonResponse,
)
async def compare_portfolio(
    userId: str,
    startDate: date = Query(...),
    endDate: date = Query(...),
    sectors: list[str] | None = Query(
        default=None
    ),
) -> PortfolioComparisonResponse:
    try:
        market_data_provider = (
            NSEMarketDataProvider()
        )

        benchmark_service = BenchmarkService(
            market_data_provider=market_data_provider
        )

        comparison_service = (
            PortfolioComparisonService(
                benchmark_service=benchmark_service
            )
        )

        return comparison_service.compare(
            user_id=userId,
            start_date=startDate,
            end_date=endDate,
            sectors=sectors,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to compare "
                "portfolio performance."
            ),
        ) from exc