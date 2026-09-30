from fastapi import APIRouter, HTTPException

from app.schemas.market_context import MarketContextResponse
from app.services.market_context_service import MarketContextService


router = APIRouter(
    prefix="/ai",
    tags=["Market Context"],
)


@router.get(
    "/market-context",
    response_model=MarketContextResponse,
)
async def get_market_context() -> MarketContextResponse:
    try:
        service = MarketContextService()

        return await service.get_market_context()

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
            detail="Unable to generate market context.",
        ) from exc