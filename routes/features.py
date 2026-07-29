from fastapi import APIRouter, HTTPException

from services.feature_service import (
    get_latest_features,
    refresh_features
)

from models.feature_models import FeatureRefreshRequest


router = APIRouter()


@router.get("/features/{userId}")
def fetch_features(userId: str):

    result = get_latest_features(userId)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Feature vector not found"
        )

    return result

@router.post("/ai/features/refresh")
def refresh_user_features(request: FeatureRefreshRequest):

    return refresh_features(request.userId)