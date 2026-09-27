from fastapi import APIRouter, BackgroundTasks

from app.ml.models.fraud import FraudCheckRequest
from app.services.fraud_inference import score_fraud_request
from app.services.fraud_alerts import publish_compliance_alert, record_fraud_alert

router = APIRouter()


@router.post("/ai/fraud-check")
def fraud_check(request: FraudCheckRequest, background_tasks: BackgroundTasks):
    result = score_fraud_request(request.model_dump())
    if result["risk_level"] == "HIGH":
        try:
            record_fraud_alert(result)
        except Exception:
            # Alert persistence should not block the fraud response.
            pass
        background_tasks.add_task(publish_compliance_alert, result)

    result["features"]["new_device"] = result["features"]["device_changed"]

    return {
        "status": "received",
        **result,
    }
