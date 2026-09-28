from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Incident:
    incident_id: str
    service_name: str
    severity: str
    description: str
    detected_at: datetime
    assigned_to: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


@dataclass
class IncidentResponse:
    incident_id: str
    service_name: str
    assigned_to: Optional[str]
    response_time_minutes: Optional[float]
    sla_minutes: int
    status: str


class OnCallService:
    def __init__(
        self,
        service_name: str,
        response_sla_minutes: int,
    ):
        if not service_name:
            raise ValueError("service_name cannot be empty")

        if response_sla_minutes <= 0:
            raise ValueError(
                "response_sla_minutes must be greater than zero"
            )

        self.service_name = service_name
        self.response_sla_minutes = response_sla_minutes
        self._incidents: dict[str, Incident] = {}

    def create_incident(
        self,
        incident_id: str,
        severity: str,
        description: str,
        detected_at: Optional[datetime] = None,
    ) -> Incident:

        if not incident_id:
            raise ValueError("incident_id cannot be empty")

        if not severity:
            raise ValueError("severity cannot be empty")

        if not description:
            raise ValueError("description cannot be empty")

        if incident_id in self._incidents:
            raise ValueError(
                f"Incident already exists: {incident_id}"
            )

        incident = Incident(
            incident_id=incident_id,
            service_name=self.service_name,
            severity=severity,
            description=description,
            detected_at=detected_at or datetime.now(timezone.utc),
        )

        self._incidents[incident_id] = incident

        return incident

    def assign_on_call(
        self,
        incident_id: str,
        engineer: str,
    ) -> Incident:

        if not engineer:
            raise ValueError("engineer cannot be empty")

        incident = self._get_incident(incident_id)
        incident.assigned_to = engineer

        return incident

    def acknowledge_incident(
        self,
        incident_id: str,
        acknowledged_at: Optional[datetime] = None,
    ) -> Incident:

        incident = self._get_incident(incident_id)

        acknowledged_at = (
            acknowledged_at or datetime.now(timezone.utc)
        )

        if acknowledged_at < incident.detected_at:
            raise ValueError(
                "acknowledged_at cannot be before detected_at"
            )

        incident.acknowledged_at = acknowledged_at

        return incident

    def evaluate_response(
        self,
        incident_id: str,
    ) -> IncidentResponse:

        incident = self._get_incident(incident_id)

        if incident.acknowledged_at is None:
            return IncidentResponse(
                incident_id=incident.incident_id,
                service_name=incident.service_name,
                assigned_to=incident.assigned_to,
                response_time_minutes=None,
                sla_minutes=self.response_sla_minutes,
                status="PENDING",
            )

        response_seconds = (
            incident.acknowledged_at - incident.detected_at
        ).total_seconds()

        response_minutes = response_seconds / 60

        status = (
            "SLA_MET"
            if response_minutes <= self.response_sla_minutes
            else "SLA_BREACHED"
        )

        return IncidentResponse(
            incident_id=incident.incident_id,
            service_name=incident.service_name,
            assigned_to=incident.assigned_to,
            response_time_minutes=response_minutes,
            sla_minutes=self.response_sla_minutes,
            status=status,
        )

    def get_incident(self, incident_id: str) -> Incident:
        return self._get_incident(incident_id)

    def _get_incident(self, incident_id: str) -> Incident:
        incident = self._incidents.get(incident_id)

        if incident is None:
            raise ValueError(
                f"Incident not found: {incident_id}"
            )

        return incident