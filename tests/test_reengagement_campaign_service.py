import pytest
from unittest.mock import AsyncMock, Mock

from app.services.reengagement_ab_test_service import (
    ABTestAssignment,
)
from app.services.reengagement_campaign_service import (
    ReengagementCampaignService,
)
from app.services.reengagement_message_service import (
    ReengagementMessageRequest,
    ReengagementMessageResponse,
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
async def test_high_risk_ai_variant_uses_llm():
    ab_test_service = Mock()
    ab_test_service.assign.return_value = ABTestAssignment(
        user_id="user-123",
        variant="ai",
    )

    template_service = Mock()

    llm_service = Mock()
    llm_service.generate = AsyncMock(
        return_value=ReengagementMessageResponse(
            userId="user-123",
            message="Continue your investment journey.",
            generatedBy="ai",
        )
    )

    service = ReengagementCampaignService(
        ab_test_service=ab_test_service,
        template_service=template_service,
        llm_service=llm_service,
    )

    result = await service.create_message(make_request(0.85))

    assert result is not None
    assert result.generatedBy == "ai"
    assert result.userId == "user-123"

    ab_test_service.assign.assert_called_once_with("user-123")
    llm_service.generate.assert_awaited_once()
    template_service.generate.assert_not_called()


@pytest.mark.asyncio
async def test_high_risk_template_variant_uses_template():
    ab_test_service = Mock()
    ab_test_service.assign.return_value = ABTestAssignment(
        user_id="user-123",
        variant="template",
    )

    template_service = Mock()
    template_service.generate.return_value = ReengagementMessageResponse(
        userId="user-123",
        message="Complete risk assessment to continue your investment journey.",
        generatedBy="template",
    )

    llm_service = Mock()

    service = ReengagementCampaignService(
        ab_test_service=ab_test_service,
        template_service=template_service,
        llm_service=llm_service,
    )

    result = await service.create_message(make_request(0.85))

    assert result is not None
    assert result.generatedBy == "template"
    assert result.userId == "user-123"

    ab_test_service.assign.assert_called_once_with("user-123")
    template_service.generate.assert_called_once()
    llm_service.generate.assert_not_called()


@pytest.mark.asyncio
async def test_score_at_threshold_is_not_high_risk():
    ab_test_service = Mock()
    template_service = Mock()
    llm_service = Mock()

    service = ReengagementCampaignService(
        ab_test_service=ab_test_service,
        template_service=template_service,
        llm_service=llm_service,
    )

    result = await service.create_message(make_request(0.7))

    assert result is None
    ab_test_service.assign.assert_not_called()
    template_service.generate.assert_not_called()


@pytest.mark.asyncio
async def test_low_risk_user_is_not_processed():
    ab_test_service = Mock()
    template_service = Mock()
    llm_service = Mock()

    service = ReengagementCampaignService(
        ab_test_service=ab_test_service,
        template_service=template_service,
        llm_service=llm_service,
    )

    result = await service.create_message(make_request(0.35))

    assert result is None
    ab_test_service.assign.assert_not_called()
    template_service.generate.assert_not_called()


@pytest.mark.asyncio
async def test_ai_variant_requires_llm_service():
    ab_test_service = Mock()
    ab_test_service.assign.return_value = ABTestAssignment(
        user_id="user-123",
        variant="ai",
    )

    service = ReengagementCampaignService(
        ab_test_service=ab_test_service,
        template_service=Mock(),
        llm_service=None,
    )

    with pytest.raises(RuntimeError, match="LLM service is required"):
        await service.create_message(make_request(0.9))