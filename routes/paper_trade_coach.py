from fastapi import APIRouter

from models.paper_trade_coach import (
    PaperTradeCoachRequest,
    PaperTradeCoachResponse,
)

from services.paper_trade_coach_service import (
    get_paper_trade_coach,
)


router = APIRouter()


@router.post(
    "/ai/paper-trade-coach",
    response_model=PaperTradeCoachResponse,
)
def paper_trade_coach(
    request: PaperTradeCoachRequest,
):

    return get_paper_trade_coach(
        request.order_id
    )