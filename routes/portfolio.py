from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.portfolio_model import PortfolioRequest
from services.portfolio_service import get_portfolio_insight
from utils.rate_limiter import check_rate_limit

router = APIRouter()


class PortfolioInsightResponse(BaseModel):
    source: str
    insight: str


@router.post("/ai/portfolio-insight", response_model=PortfolioInsightResponse)
async def generate_portfolio_insight(request: PortfolioRequest):
    if not check_rate_limit(request.user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")

    result = get_portfolio_insight(request.model_dump(), request.language)
    return result
