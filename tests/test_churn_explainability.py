from app.services.churn_service import ChurnRequest, ChurnService


def test_explain_risk_returns_existing_feature_contributions():
    service = ChurnService()

    request = ChurnRequest(
        userId="explain-user",
        features={
            "days_since_registration": 7,
            "notification_open_rate_30d": 0.10,
            "paper_trades_total": 0,
            "paper_trades_7d": 0,
            "has_real_investment": False,
        },
    )

    factors = service.explain_risk(request)

    assert len(factors) == 5

    assert {
        "factor": "New user",
        "contribution": 0.20,
    } in factors

    assert {
        "factor": "Low notification engagement",
        "contribution": 0.15,
    } in factors

    assert {
        "factor": "No paper trades",
        "contribution": 0.20,
    } in factors

    assert {
        "factor": "No paper trades in the last 7 days",
        "contribution": 0.20,
    } in factors

    assert {
        "factor": "No real investment",
        "contribution": 0.20,
    } in factors


def test_explain_risk_returns_empty_list_when_no_factors_contribute():
    service = ChurnService()

    request = ChurnRequest(
        userId="low-risk-user",
        features={
            "days_since_registration": 30,
            "notification_open_rate_30d": 0.80,
            "paper_trades_total": 20,
            "paper_trades_7d": 5,
            "has_real_investment": True,
        },
    )

    factors = service.explain_risk(request)

    assert factors == []


def test_explain_risk_supports_new_api_format():
    service = ChurnService()

    request = ChurnRequest(
        userId="new-api-user",
        daysSinceLastActivity=10,
        sessionCount7d=0,
        completedJourneySteps=1,
        totalJourneySteps=5,
        daysSinceRegistration=5,
    )

    factors = service.explain_risk(request)

    assert {
        "factor": "Recently registered",
        "contribution": 0.20,
    } in factors

    assert {
        "factor": "No sessions in the last 7 days",
        "contribution": 0.20,
    } in factors

    assert {
        "factor": "Inactive for at least 7 days",
        "contribution": 0.20,
    } in factors

    assert {
        "factor": "Incomplete journey",
        "contribution": 0.10,
    } in factors