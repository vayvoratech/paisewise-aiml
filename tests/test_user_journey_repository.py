from unittest.mock import MagicMock, patch

from app.repositories.user_journey_repository import (
    UserJourneyRepository,
)


def create_db_mock():
    db_context = MagicMock()
    connection = MagicMock()
    cursor = MagicMock()

    db_context.__enter__.return_value = connection
    db_context.__exit__.return_value = None

    connection.cursor.return_value.__enter__.return_value = cursor
    connection.cursor.return_value.__exit__.return_value = None

    return db_context, connection, cursor


def test_get_incomplete_journey_returns_incomplete_lessons():
    db_context, connection, cursor = create_db_mock()

    cursor.fetchall.return_value = [
        (
            "lesson-1",
            "IN_PROGRESS",
            4,
            10,
            40.0,
            "2026-09-08T08:00:00+00:00",
        ),
        (
            "lesson-2",
            "NOT_STARTED",
            0,
            8,
            0.0,
            "2026-09-07T08:00:00+00:00",
        ),
    ]

    with patch(
        "app.repositories.user_journey_repository.get_db",
        return_value=db_context,
    ):
        repository = UserJourneyRepository()

        result = repository.get_incomplete_journey("user-123")

    assert len(result["incomplete_steps"]) == 2

    assert result["incomplete_steps"][0]["lesson_id"] == "lesson-1"
    assert result["incomplete_steps"][0]["status"] == "IN_PROGRESS"
    assert result["incomplete_steps"][0]["current_block_index"] == 4
    assert result["incomplete_steps"][0]["total_blocks"] == 10
    assert result["incomplete_steps"][0]["scroll_position_pct"] == 40.0

    assert result["incomplete_steps"][1]["lesson_id"] == "lesson-2"
    assert result["incomplete_steps"][1]["status"] == "NOT_STARTED"

    cursor.execute.assert_called_once()


def test_get_incomplete_journey_returns_empty_when_no_progress():
    db_context, connection, cursor = create_db_mock()

    cursor.fetchall.return_value = []

    with patch(
        "app.repositories.user_journey_repository.get_db",
        return_value=db_context,
    ):
        repository = UserJourneyRepository()

        result = repository.get_incomplete_journey("user-123")

    assert result == {
        "completed_steps": [],
        "incomplete_steps": [],
    }


def test_get_incomplete_journey_filters_by_user():
    db_context, connection, cursor = create_db_mock()

    cursor.fetchall.return_value = []

    with patch(
        "app.repositories.user_journey_repository.get_db",
        return_value=db_context,
    ):
        repository = UserJourneyRepository()

        repository.get_incomplete_journey("user-456")

    cursor.execute.assert_called_once()

    args = cursor.execute.call_args.args

    assert args[1] == ("user-456",)