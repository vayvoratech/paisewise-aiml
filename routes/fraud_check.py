from fastapi import APIRouter

from models.fraud import FraudCheckRequest

router = APIRouter()


@router.post("/ai/fraud-check")
def fraud_check(request: FraudCheckRequest):
    """
    Fraud-check endpoint skeleton.

    Receives pre-computed fraud features.
    Actual fraud decision logic will be added later.
    """

    return {
        "status": "received",
        "orderId": str(request.orderId),
        "userId": str(request.userId),
        "features": request.model_dump(),
    }