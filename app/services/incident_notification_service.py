from app.services.on_call_service import OnCallService
from app.services.slack_notification_service import SlackNotificationService


class IncidentNotificationService:
    """Coordinates production incidents and Slack notifications."""

    def __init__(
        self,
        on_call_service: OnCallService,
        slack_service: SlackNotificationService,
    ) -> None:
        self.on_call_service = on_call_service
        self.slack_service = slack_service

    def notify_incident(
        self,
        incident_id: str,
        severity: str,
        description: str,
    ) -> None:
        """Create an incident and notify the on-call team."""
        incident = self.on_call_service.create_incident(
            incident_id=incident_id,
            severity=severity,
            description=description,
        )

        message = (
            "🚨 AI Service Production Incident\n\n"
            f"Incident ID: {incident.incident_id}\n"
            f"Service: {incident.service_name}\n"
            f"Severity: {incident.severity}\n"
            f"Description: {incident.description}"
        )

        self.slack_service.notify(message)