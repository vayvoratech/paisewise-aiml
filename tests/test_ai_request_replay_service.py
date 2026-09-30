from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.services.ai_request_replay_service import (
    AIRequestReplayService,
)


def test_record_and_retrieve_request():
    repository = MagicMock()

    inputs = {
        "messages": [
            {
                "role": "user",
                "content": "Explain SIP investment",
            }
        ]
    }

    recorded_at = datetime(
        2026,
        9,
        16,
        10,
        0,
        tzinfo=timezone.utc,
    )

    repository.create_request.return_value = {
        "request_id": "req-001",
        "service_name": "chat_service",
        "model": "gemini-3.5-flash-lite",
        "inputs": inputs,
        "recorded_at": recorded_at,
    }

    repository.get_request.return_value = {
        "request_id": "req-001",
        "service_name": "chat_service",
        "model": "gemini-3.5-flash-lite",
        "inputs": inputs,
        "recorded_at": recorded_at,
    }

    service = AIRequestReplayService(repository=repository)

    record = service.record_request(
        request_id="req-001",
        service_name="chat_service",
        model="gemini-3.5-flash-lite",
        inputs=inputs,
        recorded_at=recorded_at,
    )

    assert record.request_id == "req-001"
    assert record.service_name == "chat_service"
    assert record.model == "gemini-3.5-flash-lite"
    assert record.inputs == inputs
    assert record.recorded_at == recorded_at

    result = service.get_request("req-001")

    assert result.inputs == inputs

    repository.create_request.assert_called_once()
    repository.get_request.assert_called_once_with("req-001")


def test_get_replay_inputs_returns_same_inputs():
    repository = MagicMock()

    inputs = {
        "messages": [
            {
                "role": "user",
                "content": "What is diversification?",
            }
        ],
        "temperature": 0.2,
    }

    repository.create_request.return_value = {
        "request_id": "req-002",
        "service_name": "chat_service",
        "model": "gemini-3.5-flash-lite",
        "inputs": inputs,
        "recorded_at": datetime.now(timezone.utc),
    }

    repository.get_request.return_value = {
        "request_id": "req-002",
        "service_name": "chat_service",
        "model": "gemini-3.5-flash-lite",
        "inputs": inputs,
        "recorded_at": datetime.now(timezone.utc),
    }

    service = AIRequestReplayService(repository=repository)

    service.record_request(
        request_id="req-002",
        service_name="chat_service",
        model="gemini-3.5-flash-lite",
        inputs=inputs,
    )

    replay_inputs = service.get_replay_inputs("req-002")

    assert replay_inputs == inputs


def test_duplicate_request_id_is_rejected():
    repository = MagicMock()

    repository.create_request.return_value = {
        "request_id": "req-003",
        "service_name": "chat_service",
        "model": "gemini-3.5-flash-lite",
        "inputs": {"message": "hello"},
        "recorded_at": datetime.now(timezone.utc),
    }

    service = AIRequestReplayService(repository=repository)

    service.record_request(
        request_id="req-003",
        service_name="chat_service",
        model="gemini-3.5-flash-lite",
        inputs={"message": "hello"},
    )

    # Duplicate protection is now handled by PostgreSQL's
    # UNIQUE constraint rather than the old in-memory dictionary.
    repository.create_request.side_effect = ValueError(
        "Request already exists: req-003"
    )

    with pytest.raises(
        ValueError,
        match="Request already exists",
    ):
        service.record_request(
            request_id="req-003",
            service_name="chat_service",
            model="gemini-3.5-flash-lite",
            inputs={"message": "another request"},
        )


def test_missing_request_is_rejected():
    repository = MagicMock()

    repository.get_request.side_effect = ValueError(
        "AI request replay not found: unknown-request"
    )

    service = AIRequestReplayService(repository=repository)

    with pytest.raises(
        ValueError,
        match="AI request replay not found",
    ):
        service.get_request("unknown-request")


def test_empty_request_id_is_rejected():
    repository = MagicMock()

    service = AIRequestReplayService(repository=repository)

    with pytest.raises(
        ValueError,
        match="request_id cannot be empty",
    ):
        service.record_request(
            request_id="",
            service_name="chat_service",
            model="gemini-3.5-flash-lite",
            inputs={"message": "hello"},
        )