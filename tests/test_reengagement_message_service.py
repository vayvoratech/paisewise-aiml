import pytest

from app.services.reengagement_message_service import (
    ReengagementMessageRequest,
    ReengagementMessageService,
)


def test_generates_message_for_incomplete_journey() -> None:
    service = ReengagementMessageService()

    request = ReengagementMessageRequest(
        userId="user-123",
        churnScore=0.85,
        journeyContext={
            "completed_steps": ["registration"],
            "incomplete_steps": ["risk profiling"],
        },
    )

    result = service.generate(request)

    assert result.userId == "user-123"
    assert "risk profiling" in result.message
    assert result.generatedBy == "template"


def test_generates_message_when_no_incomplete_steps() -> None:
    service = ReengagementMessageService()

    request = ReengagementMessageRequest(
        userId="user-123",
        churnScore=0.80,
        journeyContext={
            "completed_steps": ["registration", "risk profiling"],
            "incomplete_steps": [],
        },
    )

    result = service.generate(request)

    assert result.userId == "user-123"
    assert result.message
    assert result.generatedBy == "template"


def test_generates_default_message_for_new_journey() -> None:
    service = ReengagementMessageService()

    request = ReengagementMessageRequest(
        userId="user-123",
        churnScore=0.90,
        journeyContext={},
    )

    result = service.generate(request)

    assert result.userId == "user-123"
    assert result.message
    assert result.generatedBy == "template"


def test_empty_user_id_is_rejected() -> None:
    service = ReengagementMessageService()

    with pytest.raises(ValueError, match="userId cannot be empty"):
        service.generate(
            ReengagementMessageRequest(
                userId=" ",
                churnScore=0.85,
                journeyContext={},
            )
        )