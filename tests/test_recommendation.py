from models.recommendation import RecommendationRequest
from services import recommendation_service


def get_test_funds():
    return [
        {
            "scheme_code": "NIPPON001",
            "scheme_name": "Nippon India Small Cap Fund",
            "category": "Equity",
            "risk_level": "High",
            "expense_ratio": 0.6,
            "aum_crore": 70000
        },
        {
            "scheme_code": "PARAG001",
            "scheme_name": "Parag Parikh Flexi Cap Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "expense_ratio": 0.4,
            "aum_crore": 60000
        },
        {
            "scheme_code": "AXIS001",
            "scheme_name": "Axis Bluechip Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "expense_ratio": 0.5,
            "aum_crore": 50000
        }
    ]


def setup_catalogue(monkeypatch):
    monkeypatch.setattr(
        recommendation_service,
        "get_catalogue",
        get_test_funds
    )

    monkeypatch.setattr(
        recommendation_service,
        "generate_fund_explanation",
        lambda fund, risk_profile: "Test explanation"
    )

    monkeypatch.setattr(
        recommendation_service,
        "create_recommendation_run",
        lambda user_id, variant: "test-run-id"
    )

    # Keep recommendation tests independent of real Redis data.
    monkeypatch.setattr(
        recommendation_service,
        "get_cached_recommendation",
        lambda user_id: None
    )


def test_high_risk_profile_gets_high_risk_fund(monkeypatch):

    setup_catalogue(monkeypatch)

    request = RecommendationRequest(
        userId="550e8400-e29b-41d4-a716-446655440000",
        riskProfile="High",
        investmentAmount=50000,
        investmentHorizon=3
    )

    result = recommendation_service.recommend_funds(request)

    assert "recommendedFunds" in result
    assert len(result["recommendedFunds"]) == 3

    assert (
        result["recommendedFunds"][0]["fundName"]
        == "Nippon India Small Cap Fund"
    )

    assert result["recommendedFunds"][0]["score"] == 50


def test_moderate_risk_profile_gets_moderate_risk_fund(monkeypatch):

    setup_catalogue(monkeypatch)

    request = RecommendationRequest(
        userId="550e8400-e29b-41d4-a716-446655440001",
        riskProfile="Moderate",
        investmentAmount=50000,
        investmentHorizon=3
    )

    result = recommendation_service.recommend_funds(request)

    assert "recommendedFunds" in result
    assert len(result["recommendedFunds"]) == 3

    assert (
        result["recommendedFunds"][0]["fundName"]
        == "Parag Parikh Flexi Cap Fund"
    )

    assert result["recommendedFunds"][0]["score"] == 50


def test_high_risk_long_term_high_amount(monkeypatch):

    setup_catalogue(monkeypatch)

    request = RecommendationRequest(
        userId="550e8400-e29b-41d4-a716-446655440002",
        riskProfile="High",
        investmentAmount=200000,
        investmentHorizon=10
    )

    result = recommendation_service.recommend_funds(request)

    assert "recommendedFunds" in result
    assert len(result["recommendedFunds"]) == 3

    assert (
        result["recommendedFunds"][0]["fundName"]
        == "Nippon India Small Cap Fund"
    )

    # +50 risk match
    # +20 long-term bonus
    # +10 high investment bonus
    assert result["recommendedFunds"][0]["score"] == 80


def test_moderate_risk_long_term_high_amount(monkeypatch):

    setup_catalogue(monkeypatch)

    request = RecommendationRequest(
        userId="550e8400-e29b-41d4-a716-446655440003",
        riskProfile="Moderate",
        investmentAmount=200000,
        investmentHorizon=10
    )

    result = recommendation_service.recommend_funds(request)

    assert "recommendedFunds" in result
    assert len(result["recommendedFunds"]) == 3

    assert (
        result["recommendedFunds"][0]["fundName"]
        == "Parag Parikh Flexi Cap Fund"
    )

    # +50 risk match
    # +20 long-term bonus
    # +10 high investment bonus
    assert result["recommendedFunds"][0]["score"] == 80


def test_no_matching_risk_profile(monkeypatch):

    setup_catalogue(monkeypatch)

    request = RecommendationRequest(
        userId="550e8400-e29b-41d4-a716-446655440004",
        riskProfile="Low",
        investmentAmount=20000,
        investmentHorizon=2
    )

    result = recommendation_service.recommend_funds(request)

    assert "recommendedFunds" in result
    assert len(result["recommendedFunds"]) == 3

    # No risk match, long-term bonus, or high-investment bonus.
    # All funds should therefore have a score of 0.
    assert all(
        fund["score"] == 0
        for fund in result["recommendedFunds"]
    )


def test_recommendation_uses_cached_result(monkeypatch):

    cached_result = {
        "recommendationRunId": "cached-run-id",
        "recommendedFunds": []
    }

    monkeypatch.setattr(
        recommendation_service,
        "get_cached_recommendation",
        lambda user_id: cached_result
    )

    def fail_if_called():
        raise AssertionError(
            "Recommendation calculation should not run on cache hit"
        )

    monkeypatch.setattr(
        recommendation_service,
        "get_catalogue",
        fail_if_called
    )

    request = RecommendationRequest(
        userId="11111111-1111-1111-1111-111111111111",
        riskProfile="Moderate",
        investmentAmount=50000,
        investmentHorizon=3
    )

    result = recommendation_service.recommend_funds(request)

    assert result == cached_result
