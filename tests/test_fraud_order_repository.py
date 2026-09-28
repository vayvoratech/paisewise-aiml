from app.repositories.fraud_order_repository import (
    FraudOrderRepository,
)


REAL_ORDER_ID = "ae55f1d8-e767-4b28-b6a9-2bbe5cf58c80"


def test_get_existing_order_by_id():
    repository = FraudOrderRepository()

    order = repository.get_order_by_id(REAL_ORDER_ID)

    assert order is not None
    assert str(order["id"]) == REAL_ORDER_ID
    assert order["symbol"] == "NSE:RELIANCE"
    assert order["side"] == "BUY"
    assert order["shares"] == 10
    assert float(order["price_per_share"]) == 2500.0
    assert float(order["total_amount"]) == 25000.0
    assert order["order_type"] == "MARKET"


def test_get_nonexistent_order_returns_none():
    repository = FraudOrderRepository()

    order = repository.get_order_by_id(
        "00000000-0000-0000-0000-000000000000"
    )

    assert order is None