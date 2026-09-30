import os
from dataclasses import dataclass
from datetime import datetime, timezone

from app.services.production_bug_repository import ProductionBugRepository


@dataclass
class ProductionBug:
    """Represents a production bug and its resolution lifecycle."""

    bug_id: str
    service_name: str
    severity: str
    description: str
    detected_at: datetime
    resolved_at: datetime | None = None


@dataclass
class BugResolution:
    """Represents the production bug resolution SLA result."""

    bug_id: str
    service_name: str
    severity: str
    resolution_time_hours: float | None
    sla_hours: float
    status: str


class ProductionBugService:
    """Tracks production bugs against a configurable resolution SLA."""

    def __init__(
        self,
        service_name: str,
        resolution_sla_hours: float | None = None,
        repository: ProductionBugRepository | None = None,
    ) -> None:
        if not service_name:
            raise ValueError("service_name cannot be empty")

        if resolution_sla_hours is None:
            resolution_sla_hours = float(
                os.getenv(
                    "PRODUCTION_BUG_RESOLUTION_SLA_HOURS",
                    "4",
                )
            )

        if resolution_sla_hours <= 0:
            raise ValueError(
                "resolution_sla_hours must be greater than zero"
            )

        self.service_name = service_name
        self.resolution_sla_hours = resolution_sla_hours
        self.repository = repository or ProductionBugRepository()

        self._bugs: dict[str, ProductionBug] = {}

    def create_bug(
        self,
        bug_id: str,
        severity: str,
        description: str,
        detected_at: datetime | None = None,
    ) -> ProductionBug:
        """Create and persist a production bug."""

        if not bug_id:
            raise ValueError("bug_id cannot be empty")

        if not severity:
            raise ValueError("severity cannot be empty")

        if not description:
            raise ValueError("description cannot be empty")

        if bug_id in self._bugs:
            raise ValueError(
                f"Production bug already exists: {bug_id}"
            )

        detected_at = detected_at or datetime.now(timezone.utc)

        bug = ProductionBug(
            bug_id=bug_id,
            service_name=self.service_name,
            severity=severity,
            description=description,
            detected_at=detected_at,
        )

        self.repository.create_bug(
            bug_id=bug.bug_id,
            service_name=bug.service_name,
            severity=bug.severity,
            description=bug.description,
            detected_at=bug.detected_at,
        )

        self._bugs[bug_id] = bug

        return bug

    def resolve_bug(
        self,
        bug_id: str,
        resolved_at: datetime | None = None,
    ) -> ProductionBug:
        """Mark and persist a production bug as resolved."""

        bug = self._get_bug(bug_id)

        resolved_at = resolved_at or datetime.now(timezone.utc)

        if resolved_at < bug.detected_at:
            raise ValueError(
                "resolved_at cannot be before detected_at"
            )

        self.repository.resolve_bug(
            bug_id=bug.bug_id,
            resolved_at=resolved_at,
        )

        bug.resolved_at = resolved_at

        return bug

    def evaluate_resolution(
        self,
        bug_id: str,
    ) -> BugResolution:
        """Evaluate the bug against the configured resolution SLA."""

        bug = self._get_bug(bug_id)

        if bug.resolved_at is None:
            return BugResolution(
                bug_id=bug.bug_id,
                service_name=bug.service_name,
                severity=bug.severity,
                resolution_time_hours=None,
                sla_hours=self.resolution_sla_hours,
                status="PENDING",
            )

        resolution_seconds = (
            bug.resolved_at - bug.detected_at
        ).total_seconds()

        resolution_hours = resolution_seconds / 3600

        status = (
            "SLA_MET"
            if resolution_hours <= self.resolution_sla_hours
            else "SLA_BREACHED"
        )

        return BugResolution(
            bug_id=bug.bug_id,
            service_name=bug.service_name,
            severity=bug.severity,
            resolution_time_hours=resolution_hours,
            sla_hours=self.resolution_sla_hours,
            status=status,
        )

    def get_bug(self, bug_id: str) -> ProductionBug:
        """Return a tracked production bug."""

        return self._get_bug(bug_id)

    def _get_bug(self, bug_id: str) -> ProductionBug:
        bug = self._bugs.get(bug_id)

        if bug is None:
            raise ValueError(
                f"Production bug not found: {bug_id}"
            )

        return bug