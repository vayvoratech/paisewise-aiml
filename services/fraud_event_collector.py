import json
import logging
import os

from kafka import KafkaConsumer

from models.fraud import OrderCreatedEvent
from services.fraud_feature_extractor import extract_fraud_features

logger = logging.getLogger(__name__)


def create_fraud_event_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        os.getenv("KAFKA_ORDERS_TOPIC", "orders.created"),
        bootstrap_servers=os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:9092",
        ),
        group_id=os.getenv(
            "KAFKA_CONSUMER_GROUP",
            "fraud-event-collector",
        ),
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        ),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )


def process_order_event(event_data: dict):
    event = OrderCreatedEvent.model_validate(event_data)

    fraud_features = extract_fraud_features(event)

    logger.info(
        "Fraud features extracted for order %s",
        fraud_features.orderId,
    )

    return fraud_features


def run_fraud_event_collector():
    consumer = create_fraud_event_consumer()

    logger.info("Fraud event collector started")

    try:
        for message in consumer:
            try:
                fraud_features = process_order_event(message.value)

                logger.info(
                    "Processed fraud event: orderId=%s, userId=%s, amount=%s",
                    fraud_features.orderId,
                    fraud_features.userId,
                    fraud_features.amount,
                )
                

            except Exception:
                logger.exception(
                    "Failed to process fraud event"
                )

    finally:
        consumer.close()

if __name__ == "__main__":
    run_fraud_event_collector()