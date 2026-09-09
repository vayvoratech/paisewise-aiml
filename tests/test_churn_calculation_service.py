from unittest.mock import Mock

from app.repositories.user_features_repository import UserFeaturesRepository
from app.services.churn_calculation_service import ChurnCalculationService
from app.services.churn_service import ChurnService


def test_calculate_for_user_updates_churn_score():
    churn_service = Mock(spec=ChurnService)
    user_features_repository = Mock(spec=UserFeaturesRepository)

    user_features_repository.get_features.return_value = {
        "user_id": "user-123",
        "days_since_registration": 7,
        "notification_open_rate_30d": 0.10,
        "paper_trades_total": 0,
        "paper_trades_7d": 0,
        "has_real_investment": False,
    }

    churn_service.calculate.return_value = Mock(
        userId="user-123",
        score=0.95,
        riskLevel="high",
    )

    service = ChurnCalculationService(
        churn_service=churn_service,
        user_features_repository=user_features_repository,
    )

    result = service.calculate_for_user("user-123")

    assert result.userId == "user-123"
    assert result.score == 0.95
    assert result.riskLevel == "high"

    user_features_repository.get_features.assert_called_once_with(
        "user-123"
    )

    churn_service.calculate.assert_called_once()

    user_features_repository.update_churn_score.assert_called_once()

    call_kwargs = (
        user_features_repository.update_churn_score.call_args.kwargs
    )

    assert call_kwargs["user_id"] == "user-123"
    assert call_kwargs["churn_score"] == 0.95
    assert call_kwargs["computed_at"] is not None


def test_calculate_for_user_raises_when_features_not_found():
    churn_service = Mock(spec=ChurnService)
    user_features_repository = Mock(spec=UserFeaturesRepository)

    user_features_repository.get_features.return_value = None

    service = ChurnCalculationService(
        churn_service=churn_service,
        user_features_repository=user_features_repository,
    )

    try:
        service.calculate_for_user("user-123")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == (
            "Churn features not found for user user-123"
        )

    churn_service.calculate.assert_not_called()
    user_features_repository.update_churn_score.assert_not_called()


def test_calculate_for_user_rejects_empty_user_id():
    service = ChurnCalculationService(
        churn_service=Mock(spec=ChurnService),
        user_features_repository=Mock(
            spec=UserFeaturesRepository
        ),
    )

    try:
        service.calculate_for_user(" ")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "user_id cannot be empty"