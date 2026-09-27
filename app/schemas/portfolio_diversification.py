from typing import Any
from pydantic import BaseModel, Field


class HoldingInput(BaseModel):
    symbol: str
    sector: str = "Unknown"
    current_value: float = Field(ge=0)


class PortfolioDiversificationRequest(BaseModel):
    holdings: list[HoldingInput]
    returns: dict[str, list[float]] = {}
    market_returns: list[float] = []


class PortfolioDiversificationResponse(BaseModel):
    diversification_score: float
    sector_concentration: dict[str, float]
    single_stock_concentration: dict[str, float]
    beta_vs_nifty: float | None
    max_drawdown: float
    correlation_matrix: dict[str, dict[str, float]]
    concentrated_bets: list[str]
