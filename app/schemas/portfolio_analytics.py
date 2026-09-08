from pydantic import BaseModel


class HoldingAnalytics(BaseModel):
    symbol: str
    shares: float
    avg_price: float
    current_price: float
    invested_value: float
    current_value: float
    pnl: float
    pnl_percentage: float


class PortfolioAnalyticsResponse(BaseModel):
    userId: str
    holdingsCount: int
    totalInvested: float
    currentValue: float
    totalPnl: float
    pnlPercentage: float
    holdings: list[HoldingAnalytics]
    healthReport: str | None = None