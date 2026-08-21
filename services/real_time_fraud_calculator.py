from models.fraud import FraudFeatures, OrderCreatedEvent


def calculate_real_time_fraud_features(
    event: OrderCreatedEvent,
    new_device: bool,
    location_changed: bool,
) -> FraudFeatures:
    """
    Calculate fraud features from an incoming order and
    already-resolved user/device/location signals.

    This function intentionally performs no database access
    so that the calculation can complete within the real-time
    latency requirement.
    """

    amount = None

    if event.price is not None:
        amount = event.quantity * event.price

    return FraudFeatures(
        orderId=event.orderId,
        userId=event.userId,
        amount=amount,
        symbol=event.symbol,
        exchange=event.exchange,
        side=event.side,
        orderType=event.orderType,
        product=event.product,
        quantity=event.quantity,
        price=event.price,
        isPaper=event.isPaper,
        placedAt=event.placedAt,
        new_device=new_device,
        location_changed=location_changed,
    )