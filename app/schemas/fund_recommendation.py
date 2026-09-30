from __future__ import annotations

from pydantic import BaseModel, Field


class FundRecommendationContext(BaseModel):
    """Optional caller-supplied context for fund recommendations."""

    goal: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    level: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )


class FundRecommendationRequest(BaseModel):
    """Input for the mutual-fund recommendation service."""

    userId: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    context: FundRecommendationContext | None = None


class FundRecommendationItem(BaseModel):
    """One recommended mutual fund."""

    schemeCode: str
    schemeName: str
    amcName: str
    category: str

    score: float

    explanation: str

    collaborativeAvailable: bool = False


class TrendingFundItem(BaseModel):
    """A fund trending among learners at the relevant level."""

    schemeCode: str
    schemeName: str
    amcName: str
    learnerLevel: str
    exposureCount: int


class FundRecommendationResponse(BaseModel):
    """Response returned by the mutual-fund recommendation endpoint."""

    userId: str

    recommendations: list[FundRecommendationItem] = Field(
        default_factory=list
    )

    trendingAmongLearners: list[TrendingFundItem] = Field(
        default_factory=list
    )