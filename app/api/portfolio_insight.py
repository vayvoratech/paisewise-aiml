from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import SessionLocal

from app.services.language_service import get_language_name, get_language_code
from app.services.portfolio_service import generate_insight

router = APIRouter()


class PortfolioInsightRequest(BaseModel):

    userId: str = Field(min_length=1)
    language: str = Field(min_length=1)
    marketContext: Optional[Dict[str, Any]] = None
    holdings: Optional[List[Dict[str, Any]]] = None


class PortfolioInsightResponse(BaseModel):
    insight: str


@router.post(
    "/ai/portfolio-insight",
    response_model=PortfolioInsightResponse,
)
def portfolio_insight(request: PortfolioInsightRequest):
    try:
        language_name = get_language_name(request.language)
        language_code = get_language_code(request.language)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    db = SessionLocal()

    try:
        row = db.execute(
            
            text("""
                SELECT
                    user_id,
                    full_name,
                    age,
                    risk_profile,
                    monthly_investment
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": request.userId},
        ).mappings().first()

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"User {request.userId} not found.",
            )

        user = dict(row)

        result = generate_insight(
            user=user,
            holdings=request.holdings or [],
            market=request.marketContext or {},
            language=language_name,
        )

        return {
            "insight": result,
        }

    except HTTPException:
        raise
    except SQLAlchemyError as error:
        print("Portfolio insight database error:", error)
        raise HTTPException(
            status_code=500,
            detail="Unable to read user data.",
        )
    except Exception as error:
        print("Portfolio insight error:", error)
        raise HTTPException(
            status_code=500,
            detail="Unable to generate portfolio insight.",
        )
    finally:
        db.close()
