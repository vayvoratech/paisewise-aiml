from typing import Any


class ChurnNotificationService:
    """
    Publishes high-risk churn notifications to Kafka.

    Only users with churn_score > 0.7 should be sent for notification.
    """

    TOPIC = "notifications.push"
    HIGH_RISK_THRESHOLD = 0.7

    def __init__(self, producer: Any) -> None:
        self.producer = producer

    def publish_if_high_risk(
        self,
        user_id: str,
        churn_score: float,
        message: str,
    ) -> bool:
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        if churn_score <= self.HIGH_RISK_THRESHOLD:
            return False

        if not message or not message.strip():
            raise ValueError("message cannot be empty")

        payload = {
            "user_id": user_id.strip(),
            "churn_score": round(float(churn_score), 4),
            "message": message.strip(),
        }

        self.producer.send(
            self.TOPIC,
            value=payload,
        )

        return True