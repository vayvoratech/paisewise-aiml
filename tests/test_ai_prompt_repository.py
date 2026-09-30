from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.services.ai_prompt_repository import AIPromptRepository


def _mock_db(columns, row):
    connection = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = row

    cursor.description = [
        type(
            "ColumnDescription",
            (),
            {"name": column},
        )()
        for column in columns
    ]

    connection.cursor.return_value = cursor

    connection.__enter__.return_value = connection
    connection.__exit__.return_value = None

    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = None

    return connection, cursor


def test_create_prompt():
    columns = [
        "id",
        "prompt_key",
        "version",
        "prompt_text",
        "is_active",
        "created_at",
        "updated_at",
    ]

    row = (
        "prompt-id",
        "chat_system_prompt",
        1,
        "Test system prompt",
        True,
        datetime.now(),
        datetime.now(),
    )

    connection, cursor = _mock_db(columns, row)

    repository = AIPromptRepository()

    with patch(
        "app.services.ai_prompt_repository.get_db",
        return_value=connection,
    ):
        result = repository.create_prompt(
            prompt_key="chat_system_prompt",
            version=1,
            prompt_text="Test system prompt",
            is_active=True,
        )

    assert result["prompt_key"] == "chat_system_prompt"
    assert result["version"] == 1
    assert result["prompt_text"] == "Test system prompt"
    assert result["is_active"] is True

    cursor.execute.assert_called_once()


def test_get_active_prompt():
    columns = [
        "id",
        "prompt_key",
        "version",
        "prompt_text",
        "is_active",
        "created_at",
        "updated_at",
    ]

    row = (
        "prompt-id",
        "chat_system_prompt",
        2,
        "Active prompt",
        True,
        datetime.now(),
        datetime.now(),
    )

    connection, cursor = _mock_db(columns, row)

    repository = AIPromptRepository()

    with patch(
        "app.services.ai_prompt_repository.get_db",
        return_value=connection,
    ):
        result = repository.get_active_prompt(
            "chat_system_prompt"
        )

    assert result["version"] == 2
    assert result["prompt_text"] == "Active prompt"
    assert result["is_active"] is True


def test_get_active_prompt_raises_when_missing():
    connection, cursor = _mock_db([], None)

    repository = AIPromptRepository()

    with patch(
        "app.services.ai_prompt_repository.get_db",
        return_value=connection,
    ):
        with pytest.raises(ValueError, match="No active AI prompt"):
            repository.get_active_prompt(
                "missing_prompt"
            )


def test_get_prompt_version():
    columns = [
        "id",
        "prompt_key",
        "version",
        "prompt_text",
        "is_active",
        "created_at",
        "updated_at",
    ]

    row = (
        "prompt-id",
        "chat_system_prompt",
        3,
        "Version 3 prompt",
        False,
        datetime.now(),
        datetime.now(),
    )

    connection, cursor = _mock_db(columns, row)

    repository = AIPromptRepository()

    with patch(
        "app.services.ai_prompt_repository.get_db",
        return_value=connection,
    ):
        result = repository.get_prompt_version(
            "chat_system_prompt",
            3,
        )

    assert result["version"] == 3
    assert result["prompt_text"] == "Version 3 prompt"


def test_get_prompt_version_raises_when_missing():
    connection, cursor = _mock_db([], None)

    repository = AIPromptRepository()

    with patch(
        "app.services.ai_prompt_repository.get_db",
        return_value=connection,
    ):
        with pytest.raises(ValueError, match="AI prompt version not found"):
            repository.get_prompt_version(
                "chat_system_prompt",
                99,
            )


def test_get_next_version():
    connection, cursor = _mock_db([], (4,))

    repository = AIPromptRepository()

    with patch(
        "app.services.ai_prompt_repository.get_db",
        return_value=connection,
    ):
        result = repository.get_next_version(
            "chat_system_prompt"
        )

    assert result == 4


def test_activate_prompt():
    columns = [
        "id",
        "prompt_key",
        "version",
        "prompt_text",
        "is_active",
        "created_at",
        "updated_at",
    ]

    row = (
        "prompt-id",
        "chat_system_prompt",
        2,
        "Version 2 prompt",
        True,
        datetime.now(),
        datetime.now(),
    )

    connection, cursor = _mock_db(columns, row)

    repository = AIPromptRepository()

    with patch(
        "app.services.ai_prompt_repository.get_db",
        return_value=connection,
    ):
        result = repository.activate_prompt(
            "chat_system_prompt",
            2,
        )

    assert result["version"] == 2
    assert result["is_active"] is True

    assert cursor.execute.call_count == 2


def test_activate_prompt_raises_when_version_missing():
    connection = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = None

    connection.__enter__.return_value = connection
    connection.__exit__.return_value = None

    connection.cursor.return_value = cursor

    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = None

    repository = AIPromptRepository()

    with patch(
        "app.services.ai_prompt_repository.get_db",
        return_value=connection,
    ):
        with pytest.raises(
            ValueError,
            match="AI prompt version not found",
        ):
            repository.activate_prompt(
                "chat_system_prompt",
                99,
            )