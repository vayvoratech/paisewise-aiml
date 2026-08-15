from datetime import datetime, timezone

from services.fraud_event_collector import process_order_event


def test_process_order_event_extracts_fraud_features():
    event_data = {
        "orderId": "11111111-1111-1111-1111-111111111111",
        "userId": "22222222-2222-2222-2222-222222222222",
        "clientOrderId": "client-order-001",
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "side": "BUY",
        "orderType": "LIMIT",
        "product": "CNC",
        "quantity": 10,
        "price": 2500.0,
        "isPaper": True,
        "placedAt": datetime.now(timezone.utc).isoformat(),
    }

    features = process_order_event(event_data)

    assert str(features.orderId) == event_data["orderId"]
    assert str(features.userId) == event_data["userId"]
    assert features.symbol == "RELIANCE"
    assert features.quantity == 10
    assert features.price == 2500.0
    assert features.amount == 25000.0