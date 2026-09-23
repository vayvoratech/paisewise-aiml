from pydantic import BaseModel, Field


class BenchmarkComparison(BaseModel):
    name: str
    returnPercentage: float
    differenceFromPortfolio: float


class PortfolioComparisonResponse(BaseModel):
    userId: str
    startDate: str
    endDate: str
    portfolioReturnPercentage: float
    benchmarks: list[BenchmarkComparison] = Field(
        default_factory=list
    )