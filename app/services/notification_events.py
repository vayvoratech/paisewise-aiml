import json
import logging
import os

logger = logging.getLogger("ai-service.notifications")


def publish_sip_report_event(user_id, report_id=None):
    """Publish a notification event when Kafka is configured; otherwise log it."""
    payload = {
        "eventType": "SIP_COACH_REPORT_READY",
        "userId": str(user_id),
        "reportId": str(report_id) if report_id is not None else None,
    }

    servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    topic = os.getenv("KAFKA_SIP_NOTIFICATION_TOPIC", "notification.events")

    if not servers:
        logger.info(
            "Kafka not configured; SIP notification event prepared: %s",
            payload,
        )
        return payload

    from kafka import KafkaProducer

    producer = KafkaProducer(
        bootstrap_servers=servers,
        security_protocol="SASL_SSL",
        sasl_mechanism="SCRAM-SHA-256",
        sasl_plain_username=os.getenv("KAFKA_USERNAME"),
        sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
        ssl_cafile="aiven-ca.pem",
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    try:
        producer.send(topic, payload).get(timeout=5)
        producer.flush()
        return payload
    finally:
        producer.close()