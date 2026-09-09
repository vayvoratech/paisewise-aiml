from typing import Any

from pydantic import BaseModel


class PortfolioAnalyticsHistoryItem(BaseModel):
    id: str
    userId: str
    snapshotDate: str
    analyticsData: dict[str, Any]
    createdAt: str


class PortfolioAnalyticsHistoryResponse(BaseModel):
    userId: str
    snapshots: list[PortfolioAnalyticsHistoryItem]