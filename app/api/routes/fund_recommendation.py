from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.fund_recommendation import (
    FundRecommendationRequest,
    FundRecommendationResponse,
)
from app.services.fund_recommendation_service import (
    FundRecommendationService,
)


router = APIRouter(
    prefix="/ai",
    tags=["Fund Recommendations"],
)


@router.post(
    "/fund-recommendations",
    response_model=FundRecommendationResponse,
)
async def get_fund_recommendations(
    request: FundRecommendationRequest,
) -> FundRecommendationResponse:
    """Return hybrid mutual-fund recommendations for a user."""

    try:
        service = FundRecommendationService()

        goal = None
        level = None

        if request.context is not None:
            goal = request.context.goal
            level = request.context.level

        return service.recommend(
            user_id=request.userId,
            goal=goal,
            level=level,
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
            detail="Unable to generate fund recommendations.",
        ) from exc