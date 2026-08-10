from fastapi import APIRouter
from models.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
)
from services.recommendation_service import recommend_funds


router = APIRouter()


@router.post(
    "/ai/fund-recommend",
    response_model=RecommendationResponse
)
def fund_recommend(request: RecommendationRequest):
    return recommend_funds(request)