from unittest.mock import MagicMock

from app.repositories.feedback_repository import FeedbackRepository
from app.services.feedback_service import FeedbackService


def test_submit_feedback_preserves_existing_behavior():
    repository = MagicMock(spec=FeedbackRepository)

    service = FeedbackService(
        feedback_repository=repository,
    )

    result = service.submit_feedback(
        response_id="response-001",
        user_id="user-001",
        category="chat",
        feedback="up",
    )

    assert result == {
        "status": "success",
        "message": "Feedback submitted successfully.",
    }

    repository.create_feedback.assert_called_once_with(
        response_id="response-001",
        user_id="user-001",
        category="chat",
        feedback="up",
    )


def test_submit_negative_feedback_preserves_existing_behavior():
    repository = MagicMock(spec=FeedbackRepository)

    service = FeedbackService(
        feedback_repository=repository,
    )

    result = service.submit_feedback(
        response_id="response-002",
        user_id="user-002",
        category="chat",
        feedback="down",
    )

    assert result == {
        "status": "success",
        "message": "Feedback submitted successfully.",
    }

    repository.create_feedback.assert_called_once_with(
        response_id="response-002",
        user_id="user-002",
        category="chat",
        feedback="down",
    )


def test_invalid_feedback_preserves_existing_validation():
    repository = MagicMock(spec=FeedbackRepository)

    service = FeedbackService(
        feedback_repository=repository,
    )

    try:
        service.submit_feedback(
            response_id="response-003",
            user_id="user-003",
            category="chat",
            feedback="invalid",
        )
    except ValueError as exc:
        assert str(exc) == "feedback must be 'up' or 'down'"
    else:
        raise AssertionError("Expected ValueError")

    repository.create_feedback.assert_not_called()