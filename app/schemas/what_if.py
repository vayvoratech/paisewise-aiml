from pydantic import BaseModel, Field


class WhatIfRequest(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)
    monthlySip: float = Field(..., gt=0)
    months: int = Field(..., gt=0)
    expectedAnnualReturn: float = Field(..., ge=0)


class WhatIfHoldingProjection(BaseModel):
    symbol: str
    currentValue: float
    allocationPercentage: float
    monthlySipAllocation: float
    additionalInvestment: float
    projectedAdditionalValue: float


class WhatIfResponse(BaseModel):
    userId: str
    monthlySip: float
    months: int
    existingPortfolioValue: float
    totalAdditionalInvestment: float
    projectedAdditionalValue: float
    projectedPortfolioValue: float
    estimatedAdditionalGain: float
    holdings: list[WhatIfHoldingProjection]