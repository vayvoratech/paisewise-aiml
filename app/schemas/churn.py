from typing import Literal

from pydantic import BaseModel, Field


class ChurnScoreRequest(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)

    daysSinceLastActivity: int = Field(..., ge=0)
    sessionCount7d: int = Field(..., ge=0)

    completedJourneySteps: int = Field(..., ge=0)
    totalJourneySteps: int = Field(..., gt=0)

    daysSinceRegistration: int = Field(..., ge=0)


class ChurnScoreResponse(BaseModel):
    userId: str
    score: float = Field(..., ge=0.0, le=1.0)
    riskLevel: Literal["low", "medium", "high"]