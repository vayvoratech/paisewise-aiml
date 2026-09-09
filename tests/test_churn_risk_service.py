from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.services.churn_risk_service import ChurnRiskService


def test_get_churn_risk_returns_high_risk():
    repository = MagicMock()

    computed_at = datetime(
        2026,
        9,
        8,
        9,
        0,
        tzinfo=timezone.utc,
    )

    repository.get_features.return_value = {
        "user_id": "user-123",
        "churn_score": 0.85,
        "churn_score_computed_at": computed_at,
    }

    service = ChurnRiskService(
        user_features_repository=repository,
    )

    result = service.get_churn_risk("user-123")

    assert result == {
        "userId": "user-123",
        "score": 0.85,
        "riskLevel": "high",
        "computedAt": computed_at,
    }

    repository.get_features.assert_called_once_with("user-123")


def test_get_churn_risk_returns_medium_risk():
    repository = MagicMock()

    repository.get_features.return_value = {
        "user_id": "user-456",
        "churn_score": 0.55,
        "churn_score_computed_at": None,
    }

    service = ChurnRiskService(
        user_features_repository=repository,
    )

    result = service.get_churn_risk("user-456")

    assert result["userId"] == "user-456"
    assert result["score"] == 0.55
    assert result["riskLevel"] == "medium"
    assert result["computedAt"] is None


def test_get_churn_risk_returns_low_risk():
    repository = MagicMock()

    repository.get_features.return_value = {
        "user_id": "user-789",
        "churn_score": 0.25,
        "churn_score_computed_at": None,
    }

    service = ChurnRiskService(
        user_features_repository=repository,
    )

    result = service.get_churn_risk("user-789")

    assert result["userId"] == "user-789"
    assert result["score"] == 0.25
    assert result["riskLevel"] == "low"


def test_get_churn_risk_raises_when_user_not_found():
    repository = MagicMock()
    repository.get_features.return_value = None

    service = ChurnRiskService(
        user_features_repository=repository,
    )

    with pytest.raises(
        LookupError,
        match="Churn risk not found for user user-123",
    ):
        service.get_churn_risk("user-123")


def test_get_churn_risk_raises_when_score_not_computed():
    repository = MagicMock()

    repository.get_features.return_value = {
        "user_id": "user-123",
        "churn_score": None,
        "churn_score_computed_at": None,
    }

    service = ChurnRiskService(
        user_features_repository=repository,
    )

    with pytest.raises(
        LookupError,
        match="Churn risk has not been computed for user user-123",
    ):
        service.get_churn_risk("user-123")


def test_get_churn_risk_rejects_empty_user_id():
    repository = MagicMock()

    service = ChurnRiskService(
        user_features_repository=repository,
    )

    with pytest.raises(
        ValueError,
        match="user_id cannot be empty",
    ):
        service.get_churn_risk("   ")

    repository.get_features.assert_not_called()