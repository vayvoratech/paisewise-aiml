from datetime import datetime, timezone

from app.services.incident_notification_service import (
    IncidentNotificationService,
)
from app.services.on_call_service import OnCallService


class FakeSlackService:
    def __init__(self):
        self.messages = []

    def notify(self, message: str) -> None:
        self.messages.append(message)


def test_incident_creates_and_sends_slack_notification():
    on_call_service = OnCallService(
        service_name="ai-service",
        response_sla_minutes=30,
    )

    slack_service = FakeSlackService()

    service = IncidentNotificationService(
        on_call_service=on_call_service,
        slack_service=slack_service,
    )

    service.notify_incident(
        incident_id="INC-001",
        severity="HIGH",
        description="AI service production error",
    )

    incident = on_call_service.get_incident("INC-001")

    assert incident.incident_id == "INC-001"
    assert incident.service_name == "ai-service"
    assert incident.severity == "HIGH"
    assert incident.description == "AI service production error"

    assert len(slack_service.messages) == 1

    message = slack_service.messages[0]

    assert "AI Service Production Incident" in message
    assert "INC-001" in message
    assert "ai-service" in message
    assert "HIGH" in message
    assert "AI service production error" in message