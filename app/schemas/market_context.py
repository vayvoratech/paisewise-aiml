from pydantic import BaseModel, Field


class MarketIndexContext(BaseModel):
    name: str
    returnPercentage: float


class MarketNewsContext(BaseModel):
    title: str
    summary: str
    source: str
    publishedAt: str
    url: str
    sentiment: str


class MarketContextResponse(BaseModel):
    asOf: str
    indices: list[MarketIndexContext] = Field(default_factory=list)
    news: list[MarketNewsContext] = Field(default_factory=list)