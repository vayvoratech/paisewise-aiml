import time
from datetime import datetime, timezone
from uuid import UUID

from models.fraud import OrderCreatedEvent
from services.real_time_fraud_calculator import (
    calculate_real_time_fraud_features,
)


def test_real_time_fraud_calculator_under_100ms():

    event = OrderCreatedEvent(
        orderId=UUID("11111111-1111-1111-1111-111111111111"),
        userId=UUID("22222222-2222-2222-2222-222222222222"),
        clientOrderId="client-test-001",
        symbol="RELIANCE",
        exchange="NSE",
        side="BUY",
        orderType="MARKET",
        product="CNC",
        quantity=10,
        price=2500,
        isPaper=False,
        placedAt=datetime.now(timezone.utc),
    )

    start = time.perf_counter()

    result = calculate_real_time_fraud_features(
        event,
        new_device=True,
        location_changed=True,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    assert result.amount == 25000
    assert result.userId == event.userId
    assert result.new_device is True
    assert result.location_changed is True

    print(f"\nReal-time fraud calculation: {elapsed_ms:.2f} ms")

    assert elapsed_ms < 100