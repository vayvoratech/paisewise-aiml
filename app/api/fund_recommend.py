from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import SessionLocal
from app.services.fund_explanation import generate_fund_reason
from app.services.fund_recommendation import get_top_recommendations
from app.services.recommendation_service import create_recommendation_run, record_recommendation_click
from app.services.recommendation_weights import get_active_weights
from app.services.language_service import get_language_name
from app.services.recommendation_ab import assign_recommendation_variant

router = APIRouter()


class FundRecommendRequest(BaseModel):
    userId: str = Field(min_length=1)
    riskProfile: str = Field(min_length=1)
    investmentAmount: float = Field(gt=0)
    investmentHorizon: int = Field(gt=0)
    userGoal: Optional[str] = None
    language: str = "English"


class KeyMetrics(BaseModel):
    riskLevel: Optional[str] = None
    category: Optional[str] = None
    return1Y: Optional[float] = None
    return3Y: Optional[float] = None
    return5Y: Optional[float] = None
    expenseRatio: Optional[float] = None
    aumCrore: Optional[float] = None


class RecommendedFund(BaseModel):
    schemeCode: str
    fundName: str
    score: float
    reason: str
    keyMetrics: KeyMetrics


class FundRecommendResponse(BaseModel):
    recommendationRunId: int
    recommendedFunds: List[RecommendedFund]


@router.post(
    "/ai/fund-recommend",
    response_model=FundRecommendResponse,
)
def recommend_funds(request: FundRecommendRequest):
    risk = request.riskProfile.strip().lower()

    try:
        language = get_language_name(request.language)
    except ValueError as error:
        if request.language.strip().lower() not in {"en", "english"}:
            raise HTTPException(status_code=400, detail=str(error))
        language = "English"

    allowed_risk_profiles = {
        "low", "moderate", "high",
        "beginner", "intermediate", "advanced",
    }

    if risk not in allowed_risk_profiles:
        raise HTTPException(
            status_code=400,
            detail=(
                "riskProfile must be Low, Moderate, High, "
                "Beginner, Intermediate, or Advanced."
            ),
        )

    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT *
                FROM mf_schemes
                WHERE is_active = TRUE
            """)
        ).mappings().all()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="No active mutual fund schemes are available.",
            )

        funds = [dict(row) for row in rows]

        top_funds = get_top_recommendations(
            funds,
            request.riskProfile,
            request.investmentHorizon,
            request.investmentAmount,
            request.userGoal,
            get_active_weights(),
        )

        if not top_funds:
            raise HTTPException(
                status_code=404,
                detail="No suitable mutual fund schemes passed the recommendation rules.",
            )

        variant = assign_recommendation_variant(request.userId)
        run_id = create_recommendation_run(
            request.userId,
            variant,
        )

        recommendations = []

        for item in top_funds:
            fund = item["fund"]

            reason = generate_fund_reason(
                fund_name=fund["scheme_name"],
                risk_level=fund.get("risk_level"),
                category=fund.get("category"),
                user_risk=request.riskProfile,
                investment_horizon=request.investmentHorizon,
                user_goal=request.userGoal,
                language=language,
            )

            recommendations.append(
                {
                    "schemeCode": str(fund["scheme_code"]),
                    "fundName": fund["scheme_name"],
                    "score": item["score"],
                    "reason": reason,
                    "keyMetrics": {
                        "riskLevel": fund.get("risk_level"),
                        "category": fund.get("category"),
                        "return1Y": fund.get("returns_1y"),
                        "return3Y": fund.get("returns_3y"),
                        "return5Y": fund.get("returns_5y"),
                        "expenseRatio": fund.get("expense_ratio"),
                        "aumCrore": fund.get("fund_size_cr"),
                    },
                }
            )

        return {
            "recommendationRunId": run_id,
            "recommendedFunds": recommendations,
        }

    except HTTPException:
        raise
    except SQLAlchemyError as error:
        print("Fund recommendation database error:", error)
        raise HTTPException(
            status_code=500,
            detail="Unable to read mutual fund data.",
        )
    except Exception as error:
        print("Fund recommendation error:", error)
        raise HTTPException(
            status_code=500,
            detail="Unable to generate fund recommendations.",
        )
    finally:
        db.close()


class RecommendationClickRequest(BaseModel):
    userId: str = Field(min_length=1)
    recommendationRunId: int
    schemeCode: str = Field(min_length=1)


@router.post("/ai/recommendation-click")
def recommendation_click(request: RecommendationClickRequest):
    try:
        click_id = record_recommendation_click(
            request.userId,
            request.recommendationRunId,
            request.schemeCode,
        )

        return {
            "clickId": click_id,
            "status": "recorded",
        }

    except Exception as error:
        print("Recommendation click error:", error)
        raise HTTPException(
            status_code=500,
            detail="Unable to record recommendation click.",
        )
