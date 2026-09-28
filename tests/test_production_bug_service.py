from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from app.services.production_bug_repository import ProductionBugRepository
from app.services.production_bug_service import ProductionBugService


# =========================================================
# Service factory
# =========================================================

def create_service():
    """
    Create an isolated ProductionBugService for unit testing.

    The repository is mocked so these tests never access
    or modify the real PostgreSQL production_bugs table.
    """

    repository = MagicMock(
        spec=ProductionBugRepository
    )

    return ProductionBugService(
        service_name="ai-service",
        resolution_sla_hours=4,
        repository=repository,
    )


# =========================================================
# Bug resolution within SLA
# =========================================================

def test_bug_resolved_within_four_hours():

    service = create_service()

    detected_at = datetime(
        2026,
        9,
        17,
        9,
        0,
        tzinfo=timezone.utc,
    )

    resolved_at = detected_at + timedelta(hours=3)

    service.create_bug(
        bug_id="BUG-001",
        severity="HIGH",
        description="AI response failure",
        detected_at=detected_at,
    )

    service.resolve_bug(
        bug_id="BUG-001",
        resolved_at=resolved_at,
    )

    result = service.evaluate_resolution(
        "BUG-001"
    )

    assert result.resolution_time_hours == 3
    assert result.sla_hours == 4
    assert result.status == "SLA_MET"


# =========================================================
# Bug resolution exceeds SLA
# =========================================================

def test_bug_resolution_exceeds_four_hours():

    service = create_service()

    detected_at = datetime(
        2026,
        9,
        17,
        9,
        0,
        tzinfo=timezone.utc,
    )

    resolved_at = detected_at + timedelta(hours=5)

    service.create_bug(
        bug_id="BUG-002",
        severity="CRITICAL",
        description="Production AI service failure",
        detected_at=detected_at,
    )

    service.resolve_bug(
        bug_id="BUG-002",
        resolved_at=resolved_at,
    )

    result = service.evaluate_resolution(
        "BUG-002"
    )

    assert result.resolution_time_hours == 5
    assert result.sla_hours == 4
    assert result.status == "SLA_BREACHED"


# =========================================================
# Unresolved bug
# =========================================================

def test_unresolved_bug_is_pending():

    service = create_service()

    service.create_bug(
        bug_id="BUG-003",
        severity="MEDIUM",
        description="Slow AI response",
    )

    result = service.evaluate_resolution(
        "BUG-003"
    )

    assert result.resolution_time_hours is None
    assert result.status == "PENDING"


# =========================================================
# SLA from environment
# =========================================================

def test_resolution_sla_can_be_read_from_environment(
    monkeypatch,
):

    monkeypatch.setenv(
        "PRODUCTION_BUG_RESOLUTION_SLA_HOURS",
        "4",
    )

    repository = MagicMock(
        spec=ProductionBugRepository
    )

    service = ProductionBugService(
        service_name="ai-service",
        repository=repository,
    )

    assert service.resolution_sla_hours == 4


# =========================================================
# Duplicate bug
# =========================================================

def test_duplicate_bug_is_rejected():

    service = create_service()

    service.create_bug(
        bug_id="BUG-004",
        severity="LOW",
        description="Test bug",
    )

    with pytest.raises(
        ValueError,
        match="Production bug already exists",
    ):
        service.create_bug(
            bug_id="BUG-004",
            severity="LOW",
            description="Duplicate bug",
        )


# =========================================================
# Invalid resolution timestamp
# =========================================================

def test_resolution_before_detection_is_rejected():

    service = create_service()

    detected_at = datetime(
        2026,
        9,
        17,
        12,
        0,
        tzinfo=timezone.utc,
    )

    service.create_bug(
        bug_id="BUG-005",
        severity="HIGH",
        description="Test production bug",
        detected_at=detected_at,
    )

    with pytest.raises(
        ValueError,
        match="resolved_at cannot be before detected_at",
    ):
        service.resolve_bug(
            bug_id="BUG-005",
            resolved_at=(
                detected_at - timedelta(hours=1)
            ),
        )