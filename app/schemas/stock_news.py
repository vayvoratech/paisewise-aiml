from pydantic import BaseModel, Field


class StockNewsItem(BaseModel):
    title: str
    summary: str
    source: str
    publishedAt: str
    url: str
    sentiment: str


class StockNewsResponse(BaseModel):
    symbol: str
    news: list[StockNewsItem] = Field(
        default_factory=list
    )