from pydantic import BaseModel
from uuid import UUID


class RecommendationRequest(BaseModel):
    userId: UUID
    riskProfile: str
    investmentAmount: float
    investmentHorizon: int


class FundKeyMetrics(BaseModel):
    riskLevel: str
    category: str
    return1Y: float | None = None
    return3Y: float | None = None
    return5Y: float | None = None
    expenseRatio: float | None = None
    aumCrore: float | None = None


class FundRecommendation(BaseModel):
    fundName: str
    score: float
    reason: str
    keyMetrics: FundKeyMetrics


class RecommendationResponse(BaseModel):
    recommendedFunds: list[FundRecommendation]