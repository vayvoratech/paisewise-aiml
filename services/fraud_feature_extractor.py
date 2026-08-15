from models.fraud import FraudFeatures, OrderCreatedEvent


def extract_fraud_features(event: OrderCreatedEvent) -> FraudFeatures:
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
    )