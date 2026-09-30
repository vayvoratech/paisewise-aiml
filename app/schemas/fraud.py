from pydantic import BaseModel, Field


class FraudScoreRequest(BaseModel):
    order_id: str = Field(min_length=1)


class FraudScoreResponse(BaseModel):
    order_id: str
    fraud_probability: float = Field(ge=0.0, le=1.0)
    decision: str