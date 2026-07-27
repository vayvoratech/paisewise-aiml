from fastapi import APIRouter
from models.portfolio_model import PortfolioRequest

from services.portfolio_service import get_portfolio_insight
from utils.rate_limiter import check_rate_limit


router = APIRouter()





@router.post("/ai/portfolio-insight")
async def generate_portfolio_insight(request: PortfolioRequest):

    allowed = check_rate_limit(request.user_id)

    if not allowed:
        return {
            "message": "Rate limit exceeded. Please try again later."
        }


    result = get_portfolio_insight(
        request.user_id,
        request.language
    )

    return result

@router.get("/portfolio/insight/{user_id}")
async def get_portfolio_insight_by_user(user_id: str):

    result = get_portfolio_insight(
        user_id,
        "english"
    )

    return result