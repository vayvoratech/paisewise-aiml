from app.services.churn_service import ChurnRequest, ChurnService


def test_high_churn_risk():
    service = ChurnService()

    request = ChurnRequest(
        userId="user-123",
        features={
            "days_since_registration": 7,
            "notification_open_rate_30d": 0.10,
            "paper_trades_total": 0,
            "paper_trades_7d": 0,
            "has_real_investment": False,
        },
    )

    result = service.calculate(request)

    assert result.userId == "user-123"
    assert result.score == 0.95
    assert result.riskLevel == "high"


def test_low_churn_risk():
    service = ChurnService()

    request = ChurnRequest(
        userId="user-456",
        features={
            "days_since_registration": 30,
            "notification_open_rate_30d": 0.80,
            "paper_trades_total": 20,
            "paper_trades_7d": 5,
            "has_real_investment": True,
        },
    )

    result = service.calculate(request)

    assert result.userId == "user-456"
    assert result.score == 0.0
    assert result.riskLevel == "low"


def test_low_churn_risk_with_some_risk_factors():
    service = ChurnService()

    request = ChurnRequest(
        userId="user-789",
        features={
            "days_since_registration": 30,
            "notification_open_rate_30d": 0.10,
            "paper_trades_total": 10,
            "paper_trades_7d": 0,
            "has_real_investment": True,
        },
    )

    result = service.calculate(request)

    assert result.userId == "user-789"
    assert result.score == 0.35
    assert result.riskLevel == "low"


def test_invalid_user_id():
    service = ChurnService()

    request = ChurnRequest(
        userId=" ",
        features={},
    )

    try:
        service.calculate(request)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "userId cannot be empty"