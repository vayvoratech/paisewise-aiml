from fastapi import APIRouter, HTTPException

from app.repositories.churn_reengagement_repository import (
    ChurnReengagementRepository,
)
from app.schemas.churn import (
    ChurnScoreRequest,
    ChurnScoreResponse,
)
from app.services.churn_risk_service import (
    ChurnRiskService,
)
from app.services.churn_service import ChurnService


router = APIRouter(
    prefix="/ai",
    tags=["Churn Risk"],
)


@router.post(
    "/churn-score",
    response_model=ChurnScoreResponse,
)
async def calculate_churn_score(
    request: ChurnScoreRequest,
) -> ChurnScoreResponse:
    try:
        service = ChurnService()
        return service.calculate(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to calculate churn score.",
        ) from exc


@router.get("/churn-risk/{userId}")
async def get_churn_risk(userId: str):
    try:
        service = ChurnRiskService()

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

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve churn risk: {exc}",
        ) from exc


@router.get("/churn-dashboard/weekly")
async def get_weekly_churn_dashboard():
    """
    Return the weekly churn-risk distribution
    for the product team dashboard.
    """

    try:
        repository = ChurnReengagementRepository()

        distribution = repository.get_weekly_churn_distribution()

        return {
            "period": "last_7_days",
            "totalUsers": distribution["total_users"],
            "distribution": {
                "low": distribution["low"],
                "medium": distribution["medium"],
                "high": distribution["high"],
            },
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate weekly churn dashboard.",
        ) from exc