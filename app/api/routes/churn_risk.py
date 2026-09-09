from fastapi import APIRouter, HTTPException

from app.services.churn_risk_service import ChurnRiskService


router = APIRouter(
    prefix="/ai",
    tags=["Churn Risk"],
)


@router.get("/churn-risk/{userId}")
def get_churn_risk(userId: str):
    service = ChurnRiskService()

    try:
        return service.get_churn_risk(userId)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc