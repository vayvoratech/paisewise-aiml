from datetime import datetime, timezone
from uuid import UUID

from models.fraud import OrderCreatedEvent
from services.fraud_feature_extractor import extract_fraud_features


def test_extract_fraud_features():
    event = OrderCreatedEvent(
        orderId=UUID("11111111-1111-1111-1111-111111111111"),
        userId=UUID("22222222-2222-2222-2222-222222222222"),
        clientOrderId="client-order-001",
        symbol="RELIANCE",
        exchange="NSE",
        side="BUY",
        orderType="LIMIT",
        product="CNC",
        quantity=10,
        price=2500.0,
        isPaper=True,
        placedAt=datetime.now(timezone.utc),
    )

    features = extract_fraud_features(event)

    assert features.orderId == event.orderId
    assert features.userId == event.userId
    assert features.symbol == "RELIANCE"
    assert features.exchange == "NSE"
    assert features.quantity == 10
    assert features.price == 2500.0
    assert features.amount == 25000.0
    assert features.isPaper is True