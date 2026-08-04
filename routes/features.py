
from fastapi import APIRouter, HTTPException

from services.feature_service import get_latest_features

router = APIRouter()


@router.get("/features/{userId}")
def fetch_features(userId: str):
    result = get_latest_features(userId)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="User features not found"
        )

    return result

