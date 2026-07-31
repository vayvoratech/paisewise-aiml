from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    userId: int
    riskProfile: str
    investmentAmount: float
    investmentHorizon: int


class FundRecommendation(BaseModel):
    fundName: str
    score: float
    reason: str


class RecommendationResponse(BaseModel):
    recommendedFunds: list[FundRecommendation]