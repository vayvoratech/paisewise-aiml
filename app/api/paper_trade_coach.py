from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.language_service import get_language_name
from app.services.llm_service import generate_portfolio_response
from app.services.paper_trade_coach import (
    build_coach_prompt,
    evaluate_trade,
    extract_trade_context,
)

router = APIRouter()


class PaperTradeCoachRequest(BaseModel):
    userId: str = Field(min_length=1)
    language: str = "English"
    order: Dict[str, Any]
    marketContext: Dict[str, Any]
    lessonHistory: Optional[List[Dict[str, Any]]] = None


class PaperTradeCoachResponse(BaseModel):
    context: Dict[str, Any]
    evaluation: Dict[str, Any]
    feedback: str


@router.post(
    "/ai/paper-trade-coach",
    response_model=PaperTradeCoachResponse,
)
def paper_trade_coach(request: PaperTradeCoachRequest):

    try:

        language = get_language_name(request.language)
    except ValueError as error:
        # English remains available as a system fallback.
        if request.language.strip().lower() not in {"en", "english"}:

            raise HTTPException(status_code=400, detail=str(error))
        language = "English"

    context = extract_trade_context(
        request.order,
        request.marketContext,
        request.lessonHistory,
    )
    
    evaluation = evaluate_trade(context)
    prompt = build_coach_prompt(context, evaluation, language)
    feedback = generate_portfolio_response(prompt)

    return {
        "context": context,
        "evaluation": evaluation,
        "feedback": feedback,
    }
