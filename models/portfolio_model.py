from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PortfolioHolding(BaseModel):
    symbol: str = Field(min_length=1)
    quantity: float = Field(gt=0)
    avg_buy_price: float | None = Field(default=None, ge=0)
    current_price: float | None = Field(default=None, ge=0)


class PortfolioRequest(BaseModel):


    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(min_length=1, alias="userId")
    language: str = "en"
    holdings: list[PortfolioHolding] = Field(default_factory=list)
    market_context: dict[str, Any] = Field(default_factory=dict, alias="marketContext")
