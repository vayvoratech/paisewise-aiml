from fastapi import APIRouter
from models.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationClickRequest,
    RecommendationClickResponse,
    RecommendationRefreshResponse,
)
from services.recommendation_service import (
    recommend_funds,
    record_recommendation_click,
)
from services.recommendation_refresh import (
    refresh_recommendation_for_lesson_completion,
    refresh_recommendation_for_goal_update,
)

router = APIRouter()


@router.post(
    "/ai/fund-recommend",
    response_model=RecommendationResponse
)
def fund_recommend(request: RecommendationRequest):
    return recommend_funds(request)

@router.post(
    "/ai/recommendation-click",
    response_model=RecommendationClickResponse
)
def recommendation_click(request: RecommendationClickRequest):

    click_id = record_recommendation_click(
        request.userId,
        request.recommendationRunId,
        request.schemeCode,
    )

    return {
        "clickId": str(click_id),
        "status": "recorded",
    }

@router.post(
    "/ai/recommendation/refresh/lesson/{userId}",
    response_model=RecommendationRefreshResponse
)
def refresh_after_lesson(userId: str):
    refresh_recommendation_for_lesson_completion(userId)

    return {
        "status": "refreshed",
        "reason": "lesson_completion",
        "userId": userId
    }


@router.post(
    "/ai/recommendation/refresh/goal/{userId}",
    response_model=RecommendationRefreshResponse
)
def refresh_after_goal_update(userId: str):
    refresh_recommendation_for_goal_update(userId)

    return {
        "status": "refreshed",
        "reason": "goal_update",
        "userId": userId
    }