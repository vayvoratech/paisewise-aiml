from pydantic import BaseModel, Field


class SIPCoachRequest(BaseModel):
    userId: str = Field(min_length=1)
    monthlySIP: float = Field(gt=0)
    targetAmount: float = Field(gt=0)
    currentAmount: float = Field(default=0, ge=0)
    monthsRemaining: int = Field(gt=0)
    expectedAnnualReturn: float = Field(default=10.0, ge=0, le=30)
    language: str = "English"


class SIPCoachResponse(BaseModel):
    userId: str
    status: str
    progressPercent: float
    projectedAmount: float
    requiredMonthlySIP: float
    monthlyGap: float
    monteCarlo: dict
    coachingAnalysis: str
