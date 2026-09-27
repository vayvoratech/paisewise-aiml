from fastapi import APIRouter
from app.schemas.portfolio_diversification import PortfolioDiversificationRequest, PortfolioDiversificationResponse
from app.services.portfolio_diversification_service import PortfolioDiversificationService

router = APIRouter(prefix="/ai", tags=["Portfolio Diversification"])
service = PortfolioDiversificationService()

@router.post("/portfolio-diversification", response_model=PortfolioDiversificationResponse)
def portfolio_diversification(request: PortfolioDiversificationRequest):
    return service.analyze(
        [item.model_dump() for item in request.holdings],
        request.returns,
        request.market_returns,
    )
