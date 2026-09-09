from unittest.mock import Mock

import pytest

from app.services.churn_notification_service import ChurnNotificationService


def test_high_risk_user_publishes_notification() -> None:
    producer = Mock()
    service = ChurnNotificationService(producer)

    result = service.publish_if_high_risk(
        user_id="user-123",
        churn_score=0.85,
        message="Complete your investment journey today.",
    )

    assert result is True

    producer.send.assert_called_once_with(
        "notifications.push",
        value={
            "user_id": "user-123",
            "churn_score": 0.85,
            "message": "Complete your investment journey today.",
        },
    )


def test_score_at_threshold_does_not_publish() -> None:
    producer = Mock()
    service = ChurnNotificationService(producer)

    result = service.publish_if_high_risk(
        user_id="user-123",
        churn_score=0.7,
        message="Complete your investment journey today.",
    )

    assert result is False
    producer.send.assert_not_called()


def test_low_risk_user_does_not_publish() -> None:
    producer = Mock()
    service = ChurnNotificationService(producer)

    result = service.publish_if_high_risk(
        user_id="user-123",
        churn_score=0.45,
        message="Complete your investment journey today.",
    )

    assert result is False
    producer.send.assert_not_called()


def test_empty_user_id_raises_error() -> None:
    producer = Mock()
    service = ChurnNotificationService(producer)

    with pytest.raises(ValueError, match="user_id cannot be empty"):
        service.publish_if_high_risk(
            user_id="",
            churn_score=0.85,
            message="Complete your investment journey today.",
        )


def test_empty_message_raises_error() -> None:
    producer = Mock()
    service = ChurnNotificationService(producer)

    with pytest.raises(ValueError, match="message cannot be empty"):
        service.publish_if_high_risk(
            user_id="user-123",
            churn_score=0.85,
            message="",
        )