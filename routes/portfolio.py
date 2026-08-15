
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.portfolio_model import PortfolioRequest
from services.portfolio_service import get_portfolio_insight
from utils.rate_limiter import check_rate_limit


router = APIRouter()


class PortfolioInsightResponse(BaseModel):
    source: str
    insight: str


@router.post(
    "/ai/portfolio-insight",
    response_model=PortfolioInsightResponse
)
async def generate_portfolio_insight(request: PortfolioRequest):

    allowed = check_rate_limit(request.user_id)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

    result = get_portfolio_insight(
        request.user_id,
        request.language
    )

    return result


@router.get(
    "/portfolio/insight/{user_id}",
    response_model=PortfolioInsightResponse
)
async def get_portfolio_insight_by_user(user_id: str):

    result = get_portfolio_insight(
        user_id,
        "en"
    )

    return result

