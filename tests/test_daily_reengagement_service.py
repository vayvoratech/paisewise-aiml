from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.daily_reengagement_service import (
    DailyReengagementService,
)


@pytest.mark.asyncio
async def test_process_uses_actual_journey_context_for_high_risk_user():
    notification_service = MagicMock()
    notification_service.process = AsyncMock(return_value=True)

    journey_repository = MagicMock()
    journey_repository.get_incomplete_journey.return_value = {
        "completed_steps": [],
        "incomplete_steps": [
            {
                "lesson_id": "lesson-1",
                "status": "IN_PROGRESS",
                "current_block_index": 4,
                "total_blocks": 10,
                "scroll_position_pct": 40.0,
            }
        ],
    }

    service = DailyReengagementService(
        notification_service=notification_service,
        journey_repository=journey_repository,
    )

    churn_result = SimpleNamespace(
        userId="user-123",
        score=0.85,
        riskLevel="high",
    )

    result = await service.process([churn_result])

    assert result == 1

    journey_repository.get_incomplete_journey.assert_called_once_with(
        "user-123"
    )

    notification_service.process.assert_awaited_once()

    request = notification_service.process.await_args.args[0]

    assert request.userId == "user-123"
    assert request.churnScore == 0.85
    assert request.journeyContext == {
        "completed_steps": [],
        "incomplete_steps": [
            {
                "lesson_id": "lesson-1",
                "status": "IN_PROGRESS",
                "current_block_index": 4,
                "total_blocks": 10,
                "scroll_position_pct": 40.0,
            }
        ],
    }


@pytest.mark.asyncio
async def test_process_skips_medium_and_low_risk_users():
    notification_service = MagicMock()
    notification_service.process = AsyncMock(return_value=True)

    journey_repository = MagicMock()

    service = DailyReengagementService(
        notification_service=notification_service,
        journey_repository=journey_repository,
    )

    churn_results = [
        SimpleNamespace(
            userId="user-1",
            score=0.70,
            riskLevel="medium",
        ),
        SimpleNamespace(
            userId="user-2",
            score=0.40,
            riskLevel="medium",
        ),
        SimpleNamespace(
            userId="user-3",
            score=0.20,
            riskLevel="low",
        ),
    ]

    result = await service.process(churn_results)

    assert result == 0
    journey_repository.get_incomplete_journey.assert_not_called()
    notification_service.process.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_handles_high_risk_user_with_empty_journey():
    notification_service = MagicMock()
    notification_service.process = AsyncMock(return_value=True)

    journey_repository = MagicMock()
    journey_repository.get_incomplete_journey.return_value = {
        "completed_steps": [],
        "incomplete_steps": [],
    }

    service = DailyReengagementService(
        notification_service=notification_service,
        journey_repository=journey_repository,
    )

    churn_result = SimpleNamespace(
        userId="user-456",
        score=0.90,
        riskLevel="high",
    )

    result = await service.process([churn_result])

    assert result == 1

    journey_repository.get_incomplete_journey.assert_called_once_with(
        "user-456"
    )

    notification_service.process.assert_awaited_once()

    request = notification_service.process.await_args.args[0]

    assert request.userId == "user-456"
    assert request.journeyContext == {
        "completed_steps": [],
        "incomplete_steps": [],
    }


@pytest.mark.asyncio
async def test_process_handles_multiple_high_risk_users():
    notification_service = MagicMock()
    notification_service.process = AsyncMock(return_value=True)

    journey_repository = MagicMock()
    journey_repository.get_incomplete_journey.side_effect = [
        {
            "completed_steps": [],
            "incomplete_steps": [{"lesson_id": "lesson-1"}],
        },
        {
            "completed_steps": ["lesson-2"],
            "incomplete_steps": [{"lesson_id": "lesson-3"}],
        },
    ]

    service = DailyReengagementService(
        notification_service=notification_service,
        journey_repository=journey_repository,
    )

    churn_results = [
        SimpleNamespace(
            userId="user-1",
            score=0.80,
            riskLevel="high",
        ),
        SimpleNamespace(
            userId="user-2",
            score=0.95,
            riskLevel="high",
        ),
    ]

    result = await service.process(churn_results)

    assert result == 2

    assert journey_repository.get_incomplete_journey.call_count == 2
    assert notification_service.process.await_count == 2