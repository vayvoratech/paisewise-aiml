from app.services.churn_service import (
    ChurnRequest,
    ChurnService,
)


def test_churn_response_contains_current_risk_summary():
    request = ChurnRequest(
        userId="explainability-test-user",
        daysSinceLastActivity=10,
        sessionCount7d=0,
        completedJourneySteps=1,
        totalJourneySteps=5,
        daysSinceRegistration=30,
    )

    response = ChurnService().calculate(request)

    assert response.userId == "explainability-test-user"
    assert isinstance(response.score, float)
    assert response.riskLevel in {
        "low",
        "medium",
        "high",
    }


def test_churn_score_reflects_existing_risk_factors():
    service = ChurnService()

    active_request = ChurnRequest(
        userId="active-user",
        daysSinceLastActivity=1,
        sessionCount7d=5,
        completedJourneySteps=5,
        totalJourneySteps=5,
        daysSinceRegistration=30,
    )

    inactive_request = ChurnRequest(
        userId="inactive-user",
        daysSinceLastActivity=10,
        sessionCount7d=0,
        completedJourneySteps=0,
        totalJourneySteps=5,
        daysSinceRegistration=5,
    )

    active_response = service.calculate(active_request)
    inactive_response = service.calculate(inactive_request)

    assert inactive_response.score > active_response.score


def test_churn_response_does_not_change_existing_contract():
    request = ChurnRequest(
        userId="contract-test-user",
        daysSinceLastActivity=3,
        sessionCount7d=2,
        completedJourneySteps=2,
        totalJourneySteps=5,
        daysSinceRegistration=20,
    )

    response = ChurnService().calculate(request)

    assert set(response.model_dump().keys()) == {
        "userId",
        "score",
        "riskLevel",
    }