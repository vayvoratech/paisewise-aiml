from datetime import datetime, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_fraud_check_endpoint():

    payload = {
        "orderId": "11111111-1111-1111-1111-111111111111",
        "userId": "22222222-2222-2222-2222-222222222222",
        "amount": 25000,
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "side": "BUY",
        "orderType": "MARKET",
        "product": "CNC",
        "quantity": 10,
        "price": 2500,
        "isPaper": False,
        "placedAt": datetime.now(timezone.utc).isoformat(),
        "new_device": True,
        "location_changed": True,
    }

    response = client.post(
        "/ai/fraud-check",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "received"
    assert data["orderId"] == payload["orderId"]
    assert data["userId"] == payload["userId"]
    assert data["features"]["new_device"] is True
    assert data["features"]["location_changed"] is True