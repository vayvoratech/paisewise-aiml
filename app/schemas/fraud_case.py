from typing import Literal

from pydantic import BaseModel


class FraudCaseDecisionRequest(BaseModel):
    decision: Literal["TRUE_FRAUD", "FALSE_POSITIVE"]


class FraudCaseDecisionResponse(BaseModel):
    case_id: str
    order_id: str
    decision: Literal["TRUE_FRAUD", "FALSE_POSITIVE"]
    status: Literal["TRUE_FRAUD", "FALSE_POSITIVE"]