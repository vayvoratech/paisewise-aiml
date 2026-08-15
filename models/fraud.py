from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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