from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.production_bug_repository import ProductionBugRepository


def _mock_db(row, columns):
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.return_value = row

    cursor.description = []

    for column in columns:
        description = MagicMock()
        description.name = column
        cursor.description.append(description)

    return connection, cursor


def test_create_bug():
    columns = [
        "id",
        "bug_id",
        "service_name",
        "severity",
        "description",
        "detected_at",
        "resolved_at",
        "created_at",
    ]

    row = (
        "db-id",
        "BUG-001",
        "ai-service",
        "HIGH",
        "AI response failure",
        datetime(2026, 9, 17, 9, 0, tzinfo=timezone.utc),
        None,
        datetime(2026, 9, 17, 9, 0, tzinfo=timezone.utc),
    )

    connection, cursor = _mock_db(row, columns)

    with patch(
        "app.services.production_bug_repository.get_db"
    ) as get_db:
        get_db.return_value.__enter__.return_value = connection

        repository = ProductionBugRepository()

        result = repository.create_bug(
            bug_id="BUG-001",
            service_name="ai-service",
            severity="HIGH",
            description="AI response failure",
            detected_at=row[5],
        )

    assert result["bug_id"] == "BUG-001"
    assert result["service_name"] == "ai-service"
    assert result["severity"] == "HIGH"
    assert result["description"] == "AI response failure"

    cursor.execute.assert_called_once()


def test_resolve_bug():
    columns = [
        "id",
        "bug_id",
        "service_name",
        "severity",
        "description",
        "detected_at",
        "resolved_at",
        "created_at",
    ]

    resolved_at = datetime(
        2026,
        9,
        17,
        12,
        0,
        tzinfo=timezone.utc,
    )

    row = (
        "db-id",
        "BUG-001",
        "ai-service",
        "HIGH",
        "AI response failure",
        datetime(2026, 9, 17, 9, 0, tzinfo=timezone.utc),
        resolved_at,
        datetime(2026, 9, 17, 9, 0, tzinfo=timezone.utc),
    )

    connection, cursor = _mock_db(row, columns)

    with patch(
        "app.services.production_bug_repository.get_db"
    ) as get_db:
        get_db.return_value.__enter__.return_value = connection

        repository = ProductionBugRepository()

        result = repository.resolve_bug(
            bug_id="BUG-001",
            resolved_at=resolved_at,
        )

    assert result["bug_id"] == "BUG-001"
    assert result["resolved_at"] == resolved_at

    cursor.execute.assert_called_once()


def test_get_bug():
    columns = [
        "id",
        "bug_id",
        "service_name",
        "severity",
        "description",
        "detected_at",
        "resolved_at",
        "created_at",
    ]

    row = (
        "db-id",
        "BUG-001",
        "ai-service",
        "HIGH",
        "AI response failure",
        datetime(2026, 9, 17, 9, 0, tzinfo=timezone.utc),
        None,
        datetime(2026, 9, 17, 9, 0, tzinfo=timezone.utc),
    )

    connection, cursor = _mock_db(row, columns)

    with patch(
        "app.services.production_bug_repository.get_db"
    ) as get_db:
        get_db.return_value.__enter__.return_value = connection

        repository = ProductionBugRepository()

        result = repository.get_bug("BUG-001")

    assert result["bug_id"] == "BUG-001"
    assert result["service_name"] == "ai-service"
    assert result["resolved_at"] is None

    cursor.execute.assert_called_once()


def test_get_bug_raises_when_not_found():
    connection, cursor = _mock_db(None, [])

    with patch(
        "app.services.production_bug_repository.get_db"
    ) as get_db:
        get_db.return_value.__enter__.return_value = connection

        repository = ProductionBugRepository()

        try:
            repository.get_bug("UNKNOWN")
            assert False
        except ValueError as exc:
            assert str(exc) == "Production bug not found: UNKNOWN"