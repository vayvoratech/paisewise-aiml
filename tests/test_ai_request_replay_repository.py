from unittest.mock import MagicMock, patch

import pytest

from app.services.ai_request_replay_repository import (
    AIRequestReplayRepository,
)


COLUMNS = [
    "id",
    "request_id",
    "service_name",
    "model",
    "inputs",
    "recorded_at",
    "created_at",
]


def _mock_db():
    connection = MagicMock()
    cursor = MagicMock()

    # Build realistic cursor.description entries.
    descriptions = []

    for column in COLUMNS:
        description = MagicMock()
        description.name = column
        descriptions.append(description)

    cursor.description = descriptions

    # Important: repository uses:
    # with connection.cursor() as cursor:
    connection.cursor.return_value.__enter__.return_value = cursor

    # Important: get_db() itself is also used as:
    # with get_db() as connection:
    connection.__enter__.return_value = connection
    connection.__exit__.return_value = False

    return connection, cursor


def test_create_request():
    connection, cursor = _mock_db()

    row = (
        "db-id",
        "req-001",
        "chat_service",
        "gemini-3.5-flash-lite",
        {"message": "hello"},
        "2026-09-16T10:00:00Z",
        "2026-09-16T10:00:00Z",
    )

    cursor.fetchone.return_value = row

    repository = AIRequestReplayRepository()

    with patch(
        "app.services.ai_request_replay_repository.get_db",
        return_value=connection,
    ):
        result = repository.create_request(
            request_id="req-001",
            service_name="chat_service",
            model="gemini-3.5-flash-lite",
            inputs={"message": "hello"},
            recorded_at="2026-09-16T10:00:00Z",
        )

    assert result == dict(zip(COLUMNS, row))
    assert result["request_id"] == "req-001"
    assert result["service_name"] == "chat_service"
    assert result["model"] == "gemini-3.5-flash-lite"
    assert result["inputs"] == {"message": "hello"}

    cursor.execute.assert_called_once()


def test_get_request():
    connection, cursor = _mock_db()

    row = (
        "db-id",
        "req-002",
        "chat_service",
        "gemini-3.5-flash-lite",
        {"message": "Explain SIP"},
        "2026-09-16T10:00:00Z",
        "2026-09-16T10:00:00Z",
    )

    cursor.fetchone.return_value = row

    repository = AIRequestReplayRepository()

    with patch(
        "app.services.ai_request_replay_repository.get_db",
        return_value=connection,
    ):
        result = repository.get_request("req-002")

    assert result == dict(zip(COLUMNS, row))
    assert result["request_id"] == "req-002"
    assert result["service_name"] == "chat_service"
    assert result["model"] == "gemini-3.5-flash-lite"
    assert result["inputs"] == {"message": "Explain SIP"}

    cursor.execute.assert_called_once_with(
        """
            SELECT
                id,
                request_id,
                service_name,
                model,
                inputs,
                recorded_at,
                created_at
            FROM public.ai_request_replays
            WHERE request_id = %s
        """,
        ("req-002",),
    )


def test_get_request_not_found():
    connection, cursor = _mock_db()

    cursor.fetchone.return_value = None

    repository = AIRequestReplayRepository()

    with patch(
        "app.services.ai_request_replay_repository.get_db",
        return_value=connection,
    ):
        with pytest.raises(
            ValueError,
            match="AI request replay not found: unknown-request",
        ):
            repository.get_request("unknown-request")