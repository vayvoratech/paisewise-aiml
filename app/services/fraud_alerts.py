import json
import logging
import os

logger = logging.getLogger("ai-service.fraud-alerts")


def publish_compliance_alert(result):
    payload = {
        "eventType": "HIGH_RISK_FRAUD_ALERT",
        "orderId": result["orderId"],
        "userId": result["userId"],
        "riskScore": result["risk_score"],
        "riskLevel": result["risk_level"],
        "triggeredFlags": result["triggered_flags"],
    }
    servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not servers:
        logger.info("Kafka not configured; compliance alert prepared: %s", payload)
        return payload
    from kafka import KafkaProducer
    producer = KafkaProducer(
        bootstrap_servers=servers,
        security_protocol="SASL_SSL",
        sasl_mechanism="SCRAM-SHA-256",
        sasl_plain_username=os.getenv("KAFKA_USERNAME"),
        sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
        ssl_cafile="aiven-ca.pem",
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    try:
        producer.send(os.getenv("KAFKA_COMPLIANCE_TOPIC", "compliance.alerts"), payload).get(timeout=5)
        producer.flush()
    finally:
        producer.close()
    return payload


def record_fraud_alert(result):
    from database.database import get_db_connection
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO audit_log (user_id, action, entity_type, entity_id, new_values, result)
                VALUES (%s, %s, %s, NULL, %s::jsonb, %s)
            """, (result["userId"], "FRAUD_HIGH_RISK", "ORDER", json.dumps(result), "SUCCESS"))
        connection.commit()
    finally:
        connection.close()


def get_recent_fraud_alerts(limit=100):
    from database.database import get_db_connection
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, action, entity_id, new_values, created_at
                FROM audit_log
                WHERE action IN ('FRAUD_HIGH_RISK', 'FRAUD_ALERT')
                ORDER BY created_at DESC LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            return [{"id": r[0], "userId": str(r[1]) if r[1] else None, "action": r[2], "entityId": str(r[3]) if r[3] else None, "details": r[4], "createdAt": r[5].isoformat() if r[5] else None} for r in rows]
    finally:
        connection.close()
