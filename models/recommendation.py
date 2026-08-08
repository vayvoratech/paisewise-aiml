from pydantic import BaseModel

from uuid import UUID

class RecommendationRequest(BaseModel):
    userId: UUID
    riskProfile: str
    investmentAmount: float
    investmentHorizon: int


class FundRecommendation(BaseModel):
    fundName: str
    score: float
    reason: str
    keyMetrics: dict


class RecommendationResponse(BaseModel):
    recommendedFunds: list[FundRecommendation]