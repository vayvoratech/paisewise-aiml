
import logging
from services.fraud_model import get_fraud_model
from app.services.fraud_detection import evaluate_fraud_event

logger = logging.getLogger("ai-service.fraud")
FEATURE_ORDER = [
    "device_changed", "location_changed", "time_since_registration",
    "order_value", "orders_last_30min", "failed_mpin_count_24hr", "login_count_today",
]


def _model_risk(features: dict) -> float:
    model = get_fraud_model()
    if model is None:
        return 0.0
    values = [[
        float(bool(features["device_changed"])),
        float(bool(features["location_changed"])),
        float(features["time_since_registration"]),
        float(features["order_value"]),
        float(features["orders_last_30min"]),
        float(features["failed_mpin_count_24hr"]),
        float(features["login_count_today"]),
    ]]
    # IsolationForest decision_function: lower is more anomalous.
    decision = float(model.decision_function(values)[0])
    return max(0.0, min(100.0, 50.0 - decision * 100.0))


def score_fraud_request(request: dict) -> dict:
    event = {
        "device_changed": request.get("new_device", False),
        "location_changed": request.get("location_changed", False),
        "time_since_registration": request.get("time_since_registration", 9999),
        "order_value": request.get("amount") or 0,
        "orders_last_30min": request.get("orders_last_30min", 0),
        "failed_mpin_count_24hr": request.get("failed_mpin_count_24hr", 0),
        "login_count_today": request.get("login_count_today", 0),
    }
    evaluation = evaluate_fraud_event(event)
    risk = _model_risk(evaluation["features"])
    if evaluation["triggered_categories"]:
        risk = max(risk, min(100.0, 70.0 + 5.0 * len(evaluation["triggered_categories"])))
    risk = round(risk, 2)
    if risk > 70:
        level = "HIGH"
    elif risk >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"
    return {
        "orderId": str(request["orderId"]),
        "userId": str(request["userId"]),
        "risk_score": risk,
        "risk_level": level,
        "triggered_flags": evaluation["triggered_categories"],
        "features": evaluation["features"],
    }
