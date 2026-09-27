from fastapi import APIRouter
from app.services.fraud_alerts import get_recent_fraud_alerts

router = APIRouter()


@router.get("/ai/fraud-alerts")
def fraud_alerts(limit: int = 100):
    return {"alerts": get_recent_fraud_alerts(max(1, min(limit, 500)))}
