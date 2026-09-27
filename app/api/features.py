from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.pipelines.feature_pipeline import run_behaviour_feature_pipeline
from app.services.feature_service import get_latest_features

router = APIRouter()


class FeatureResponse(BaseModel):
    user_id: str
    features: dict
    feature_version: str | None = None
    updated_at: str | None = None


@router.get("/features/{userId}", response_model=FeatureResponse)
def fetch_features(userId: str):
    result = get_latest_features(userId)
    if result is None:
        raise HTTPException(status_code=404, detail="User features not found")
    return result


@router.post("/ai/features/refresh/{userId}")
def refresh_features(userId: str):
    # The existing pipeline is incremental and user-aware. Running it here
    # recalculates users with new activity and keeps the same feature logic.
    try:
        updated = run_behaviour_feature_pipeline(full_refresh=False)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Feature refresh failed: {error}")
    latest = get_latest_features(userId)
    if latest is None:
        raise HTTPException(status_code=404, detail="User features not found after refresh")
    return {"status": "refreshed", "userId": userId, "updatedUsers": updated, **latest}
