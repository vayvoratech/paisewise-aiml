from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OrderCreatedEvent(BaseModel):
    orderId: UUID
    userId: UUID
    clientOrderId: str
    symbol: str
    exchange: str
    side: str
    orderType: str
    product: str
    quantity: float
    price: float | None = None
    isPaper: bool
    placedAt: datetime


class FraudFeatures(BaseModel):
    orderId: UUID
    userId: UUID
    amount: float | None = None
    symbol: str
    exchange: str
    side: str
    orderType: str
    product: str
    quantity: float
    price: float | None = None
    isPaper: bool
    placedAt: datetime
    new_device: bool = False
    location_changed: bool = False
    time_since_registration: int = 9999
    orders_last_30min: int = 0
    failed_mpin_count_24hr: int = 0
    login_count_today: int = 0


class FraudCheckRequest(BaseModel):
    orderId: UUID
    userId: UUID
    amount: float | None = Field(default=None, ge=0)
    symbol: str = Field(min_length=1)
    exchange: str = Field(min_length=1)
    side: str = Field(min_length=1)
    orderType: str = Field(min_length=1)
    product: str = Field(min_length=1)
    quantity: float = Field(gt=0)
    price: float | None = Field(default=None, ge=0)
    isPaper: bool
    placedAt: datetime
    new_device: bool = False
    location_changed: bool = False
    time_since_registration: int = Field(default=9999, ge=0)
    orders_last_30min: int = Field(default=0, ge=0)
    failed_mpin_count_24hr: int = Field(default=0, ge=0)
    login_count_today: int = Field(default=0, ge=0)
