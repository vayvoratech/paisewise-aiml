import pytest
from unittest.mock import AsyncMock, Mock

from app.services.reengagement_message_service import (
    ReengagementMessageRequest,
    ReengagementMessageResponse,
)
from app.services.reengagement_notification_service import (
    ReengagementNotificationService,
)


def make_request(churn_score: float) -> ReengagementMessageRequest:
    return ReengagementMessageRequest(
        userId="user-123",
        churnScore=churn_score,
        journeyContext={
            "completed_steps": ["registration"],
            "incomplete_steps": ["risk assessment"],
        },
    )


@pytest.mark.asyncio
async def test_high_risk_user_message_is_published():
    campaign_service = Mock()
    campaign_service.create_message = AsyncMock(
        return_value=ReengagementMessageResponse(
            userId="user-123",
            message="Complete your risk assessment to continue.",
            generatedBy="ai",
        )
    )

    notification_service = Mock()
    notification_service.publish_if_high_risk.return_value = True

    service = ReengagementNotificationService(
        campaign_service=campaign_service,
        notification_service=notification_service,
    )

    result = await service.process(make_request(0.85))

    assert result is True

    campaign_service.create_message.assert_awaited_once()

    notification_service.publish_if_high_risk.assert_called_once_with(
        user_id="user-123",
        churn_score=0.85,
        message="Complete your risk assessment to continue.",
    )


@pytest.mark.asyncio
async def test_non_high_risk_user_is_not_published():
    campaign_service = Mock()
    campaign_service.create_message = AsyncMock(
        return_value=None
    )

    notification_service = Mock()

    service = ReengagementNotificationService(
        campaign_service=campaign_service,
        notification_service=notification_service,
    )

    result = await service.process(make_request(0.65))

    assert result is False

    campaign_service.create_message.assert_awaited_once()
    notification_service.publish_if_high_risk.assert_not_called()


@pytest.mark.asyncio
async def test_notification_failure_returns_false():
    campaign_service = Mock()
    campaign_service.create_message = AsyncMock(
        return_value=ReengagementMessageResponse(
            userId="user-123",
            message="Continue your investment journey.",
            generatedBy="template",
        )
    )

    notification_service = Mock()
    notification_service.publish_if_high_risk.return_value = False

    service = ReengagementNotificationService(
        campaign_service=campaign_service,
        notification_service=notification_service,
    )

    result = await service.process(make_request(0.9))

    assert result is False

    notification_service.publish_if_high_risk.assert_called_once_with(
        user_id="user-123",
        churn_score=0.9,
        message="Continue your investment journey.",
    )


@pytest.mark.asyncio
async def test_ai_and_template_messages_both_reach_notification_service():
    campaign_service = Mock()
    campaign_service.create_message = AsyncMock(
        return_value=ReengagementMessageResponse(
            userId="user-123",
            message="Your personalized message.",
            generatedBy="ai",
        )
    )

    notification_service = Mock()
    notification_service.publish_if_high_risk.return_value = True

    service = ReengagementNotificationService(
        campaign_service=campaign_service,
        notification_service=notification_service,
    )

    result = await service.process(make_request(0.95))

    assert result is True
    notification_service.publish_if_high_risk.assert_called_once()