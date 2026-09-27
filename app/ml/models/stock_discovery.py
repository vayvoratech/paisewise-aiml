from pydantic import BaseModel, Field
from pydantic import ConfigDict


class StockDiscoveryResponse(BaseModel):
    userId: str
    learningLevel: int
    stocks: list[dict]
    disclaimer: str


class StockDiscoveryRequest(BaseModel):
    userId: str = Field(min_length=1)
    riskProfile: str = "moderate"
    learningLevel: int = Field(default=5, ge=1, le=10)
    completedLessons: list[str] = Field(default_factory=list)
