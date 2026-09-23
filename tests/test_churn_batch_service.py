from datetime import date
from unittest.mock import Mock

from app.repositories.user_repository import UserRepository
from app.services.churn_batch_service import ChurnBatchService
from app.services.churn_calculation_service import ChurnCalculationService
from app.services.churn_service import ChurnResponse


def test_calculates_churn_for_users_registered_seven_days_ago():
    user_repository = Mock(spec=UserRepository)
    churn_calculation_service = Mock(
        spec=ChurnCalculationService
    )

    user_repository.get_users_registered_on.return_value = [
        {
            "id": "user-001",
            "name": "User One",
        },
        {
            "id": "user-002",
            "name": "User Two",
        },
    ]

    churn_calculation_service.calculate_for_user.side_effect = [
        ChurnResponse(
            userId="user-001",
            score=0.8,
            riskLevel="high",
        ),
        ChurnResponse(
            userId="user-002",
            score=0.2,
            riskLevel="low",
        ),
    ]

    service = ChurnBatchService(
        user_repository=user_repository,
        churn_calculation_service=churn_calculation_service,
    )

    results = service.calculate_for_users_registered_seven_days_ago(
        today=date(2026, 9, 8)
    )

    assert len(results) == 2

    assert results[0].userId == "user-001"
    assert results[0].score == 0.8
    assert results[0].riskLevel == "high"

    assert results[1].userId == "user-002"
    assert results[1].score == 0.2
    assert results[1].riskLevel == "low"

    user_repository.get_users_registered_on.assert_called_once_with(
        date(2026, 9, 1)
    )

    assert churn_calculation_service.calculate_for_user.call_count == 2


def test_returns_empty_list_when_no_users_registered():
    user_repository = Mock(spec=UserRepository)
    churn_calculation_service = Mock(
        spec=ChurnCalculationService
    )

    user_repository.get_users_registered_on.return_value = []

    service = ChurnBatchService(
        user_repository=user_repository,
        churn_calculation_service=churn_calculation_service,
    )

    results = service.calculate_for_users_registered_seven_days_ago(
        today=date(2026, 9, 8)
    )

    assert results == []

    user_repository.get_users_registered_on.assert_called_once_with(
        date(2026, 9, 1)
    )

    churn_calculation_service.calculate_for_user.assert_not_called()


def test_skips_users_without_churn_features():
    user_repository = Mock(spec=UserRepository)
    churn_calculation_service = Mock(
        spec=ChurnCalculationService
    )

    user_repository.get_users_registered_on.return_value = [
        {"id": "user-001"},
        {"id": "user-002"},
    ]

    churn_calculation_service.calculate_for_user.side_effect = [
        ValueError("Churn features not found"),
        ChurnResponse(
            userId="user-002",
            score=0.75,
            riskLevel="high",
        ),
    ]

    service = ChurnBatchService(
        user_repository=user_repository,
        churn_calculation_service=churn_calculation_service,
    )

    results = service.calculate_for_users_registered_seven_days_ago(
        today=date(2026, 9, 8)
    )

    assert len(results) == 1
    assert results[0].userId == "user-002"
    assert results[0].score == 0.75
    assert results[0].riskLevel == "high"

    assert churn_calculation_service.calculate_for_user.call_count == 2