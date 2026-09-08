from fastapi import APIRouter

from models.fraud import FraudCheckRequest
from services.fraud_inference import score_fraud_request

router = APIRouter()


@router.post("/ai/fraud-check")
def fraud_check(request: FraudCheckRequest):
    result = score_fraud_request(request.model_dump())

    result["features"]["new_device"] = result["features"]["device_changed"]

    return {
        "status": "received",
        **result,
    }
