from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.stock_discovery_service import StockDiscoveryService


router = APIRouter(
    prefix="/ai",
    tags=["Stock Discovery"],
)


class StockDiscoveryNewsItem(BaseModel):
    title: str
    summary: str
    source: str
    publishedAt: str
    url: str
    sentiment: str


class StockDiscoveryItem(BaseModel):
    symbol: str
    companyName: str
    sector: str
    price: float | None = None
    changePct: float | None = None
    emoji: str | None = None
    news: list[StockDiscoveryNewsItem] = Field(
        default_factory=list
    )


class StockDiscoveryResponse(BaseModel):
    userId: str
    stocks: list[StockDiscoveryItem] = Field(
        default_factory=list
    )


@router.get(
    "/stock-discovery/{userId}",
    response_model=StockDiscoveryResponse,
)
async def get_stock_discovery(
    userId: str,
) -> StockDiscoveryResponse:

    if not userId or not userId.strip():
        raise HTTPException(
            status_code=400,
            detail="userId cannot be empty",
        )

    try:
        service = StockDiscoveryService()

        stocks = await service.discover(
            user_id=userId.strip()
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
            detail="Unable to generate stock discovery.",
        ) from exc

    return StockDiscoveryResponse(
        userId=userId.strip(),
        stocks=stocks,
    )