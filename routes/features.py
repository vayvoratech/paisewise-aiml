
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.feature_service import get_latest_features


router = APIRouter()


class FeatureValues(BaseModel):
    quiz_attempts_total: int | None = None
    quiz_pass_rate: float | None = None
    avg_quiz_score: float | None = None


class FeatureResponse(BaseModel):
    user_id: str
    features: FeatureValues
    updated_at: str | None = None


@router.get(
    "/features/{userId}",
    response_model=FeatureResponse
)
def fetch_features(userId: str):

    result = get_latest_features(userId)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="User features not found"
        )

    return result

