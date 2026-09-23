from fastapi import APIRouter, HTTPException

from app.schemas.portfolio_analytics_history import (
    PortfolioAnalyticsHistoryResponse,
)
from app.services.portfolio_analytics_history_service import (
    PortfolioAnalyticsHistoryService,
)


router = APIRouter(
    prefix="/ai",
    tags=["Portfolio Analytics"],
)


@router.get(
    "/portfolio-analytics/history/{userId}",
    response_model=PortfolioAnalyticsHistoryResponse,
)
async def get_portfolio_analytics_history(
    userId: str,
) -> PortfolioAnalyticsHistoryResponse:
    try:
        service = PortfolioAnalyticsHistoryService()

        return service.get_history(
            user_id=userId
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
                "Unable to retrieve "
                "portfolio analytics history."
            ),
        ) from exc