import pytest

from models.recommendation import RecommendationRequest
from services import recommendation_service


def test_high_risk_profile_gets_high_risk_fund(monkeypatch):

    # Fake fund catalogue for testing
    test_funds = [
        {
            "scheme_name": "Nippon India Small Cap Fund",
            "category": "Equity",
            "risk_level": "High",
            "return_1y": 12,
            "return_3y": 15,
            "return_5y": 18,
            "sharpe_ratio": 1.2,
            "expense_ratio": 0.5,
            "aum_crore": 10000
        },
        {
            "scheme_name": "Parag Parikh Flexi Cap Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "return_1y": 10,
            "return_3y": 13,
            "return_5y": 16,
            "sharpe_ratio": 1.1,
            "expense_ratio": 0.4,
            "aum_crore": 50000
        },
        {
            "scheme_name": "Axis Bluechip Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "return_1y": 8,
            "return_3y": 11,
            "return_5y": 14,
            "sharpe_ratio": 1.0,
            "expense_ratio": 0.6,
            "aum_crore": 30000
        }
    ]

    # Replace actual catalogue with our test catalogue
    monkeypatch.setattr(
        recommendation_service,
        "get_catalogue",
        lambda: test_funds
    )

    # Avoid calling the actual LLM
    monkeypatch.setattr(
        recommendation_service,
        "generate_fund_explanation",
        lambda fund, risk_profile: "Test explanation"
    )

    # Create a high-risk user
    request = RecommendationRequest(
        userId="550e8400-e29b-41d4-a716-446655440000",
        riskProfile="High",
        investmentAmount=50000,
        investmentHorizon=3
    )

    # Call recommendation logic
    result = recommendation_service.recommend_funds(request)

    # Verify response contains recommendations
    assert "recommendedFunds" in result

    # Verify 3 funds are returned
    assert len(result["recommendedFunds"]) == 3

    # Verify the first recommendation is the high-risk fund
    assert (
        result["recommendedFunds"][0]["fundName"]
        == "Nippon India Small Cap Fund"
    )

def test_moderate_risk_profile_gets_moderate_risk_fund(monkeypatch):

    test_funds = [
        {
            "scheme_name": "Nippon India Small Cap Fund",
            "category": "Equity",
            "risk_level": "High",
            "return_1y": 12,
            "return_3y": 15,
            "return_5y": 18,
            "sharpe_ratio": 1.2,
            "expense_ratio": 0.5,
            "aum_crore": 10000
        },
        {
            "scheme_name": "Parag Parikh Flexi Cap Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "return_1y": 10,
            "return_3y": 13,
            "return_5y": 16,
            "sharpe_ratio": 1.1,
            "expense_ratio": 0.4,
            "aum_crore": 50000
        },
        {
            "scheme_name": "Axis Bluechip Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "return_1y": 8,
            "return_3y": 11,
            "return_5y": 14,
            "sharpe_ratio": 1.0,
            "expense_ratio": 0.6,
            "aum_crore": 30000
        }
    ]

    monkeypatch.setattr(
        recommendation_service,
        "get_catalogue",
        lambda: test_funds
    )

    monkeypatch.setattr(
        recommendation_service,
        "generate_fund_explanation",
        lambda fund, risk_profile: "Test explanation"
    )

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

def test_high_risk_long_term_high_amount(monkeypatch):

    test_funds = [
        {
            "scheme_name": "Nippon India Small Cap Fund",
            "category": "Equity",
            "risk_level": "High",
            "return_1y": 12,
            "return_3y": 15,
            "return_5y": 18,
            "sharpe_ratio": 1.2,
            "expense_ratio": 0.5,
            "aum_crore": 10000
        },
        {
            "scheme_name": "Parag Parikh Flexi Cap Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "return_1y": 10,
            "return_3y": 13,
            "return_5y": 16,
            "sharpe_ratio": 1.1,
            "expense_ratio": 0.4,
            "aum_crore": 50000
        },
        {
            "scheme_name": "Axis Bluechip Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "return_1y": 8,
            "return_3y": 11,
            "return_5y": 14,
            "sharpe_ratio": 1.0,
            "expense_ratio": 0.6,
            "aum_crore": 30000
        }
    ]

    monkeypatch.setattr(
        recommendation_service,
        "get_catalogue",
        lambda: test_funds
    )

    monkeypatch.setattr(
        recommendation_service,
        "generate_fund_explanation",
        lambda fund, risk_profile: "Test explanation"
    )

    request = RecommendationRequest(
        userId="550e8400-e29b-41d4-a716-446655440002",
        riskProfile="High",
        investmentAmount=200000,
        investmentHorizon=10
    )

    result = recommendation_service.recommend_funds(request)

    assert "recommendedFunds" in result
    assert len(result["recommendedFunds"]) == 3

    # High-risk fund should be ranked first
    assert (
        result["recommendedFunds"][0]["fundName"]
        == "Nippon India Small Cap Fund"
    )

    # Verify the score includes:
    # +50 risk match
    # +12 return
    # +20 long-term bonus
    # +10 high investment bonus
    assert result["recommendedFunds"][0]["score"] == 92

def test_moderate_risk_long_term_high_amount(monkeypatch):

    test_funds = [
        {
            "scheme_name": "Nippon India Small Cap Fund",
            "category": "Equity",
            "risk_level": "High",
            "return_1y": 12,
            "return_3y": 15,
            "return_5y": 18,
            "sharpe_ratio": 1.2,
            "expense_ratio": 0.5,
            "aum_crore": 10000
        },
        {
            "scheme_name": "Parag Parikh Flexi Cap Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "return_1y": 10,
            "return_3y": 13,
            "return_5y": 16,
            "sharpe_ratio": 1.1,
            "expense_ratio": 0.4,
            "aum_crore": 50000
        },
        {
            "scheme_name": "Axis Bluechip Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "return_1y": 8,
            "return_3y": 11,
            "return_5y": 14,
            "sharpe_ratio": 1.0,
            "expense_ratio": 0.6,
            "aum_crore": 30000
        }
    ]

    monkeypatch.setattr(
        recommendation_service,
        "get_catalogue",
        lambda: test_funds
    )

    monkeypatch.setattr(
        recommendation_service,
        "generate_fund_explanation",
        lambda fund, risk_profile: "Test explanation"
    )

    request = RecommendationRequest(
        userId="550e8400-e29b-41d4-a716-446655440003",
        riskProfile="Moderate",
        investmentAmount=200000,
        investmentHorizon=10
    )

    result = recommendation_service.recommend_funds(request)

    assert "recommendedFunds" in result
    assert len(result["recommendedFunds"]) == 3

    # Moderate + long-term investor should get Parag first
    assert (
        result["recommendedFunds"][0]["fundName"]
        == "Parag Parikh Flexi Cap Fund"
    )

    # Verify scoring logic
    assert result["recommendedFunds"][0]["score"] == 90

def test_no_matching_risk_profile_uses_return_score(monkeypatch):

    test_funds = [
        {
            "scheme_name": "Nippon India Small Cap Fund",
            "category": "Equity",
            "risk_level": "High",
            "return_1y": 12,
            "return_3y": 15,
            "return_5y": 18,
            "sharpe_ratio": 1.2,
            "expense_ratio": 0.5,
            "aum_crore": 10000
        },
        {
            "scheme_name": "Parag Parikh Flexi Cap Fund",
            "category": "Equity",
            "risk_level": "Moderate",
            "return_1y": 10,
            "return_3y": 13,
            "return_5y": 16,
            "sharpe_ratio": 1.1,
            "expense_ratio": 0.4,
            "aum_crore": 50000
        },
        {
            "scheme_name": "Axis Bluechip Fund",
            "category": "Equity",
            "return_1y": 8,
            "return_3y": 11,
            "return_5y": 14,
            "risk_level": "Moderate",
            "sharpe_ratio": 1.0,
            "expense_ratio": 0.6,
            "aum_crore": 30000
        }
    ]

    monkeypatch.setattr(
        recommendation_service,
        "get_catalogue",
        lambda: test_funds
    )

    monkeypatch.setattr(
        recommendation_service,
        "generate_fund_explanation",
        lambda fund, risk_profile: "Test explanation"
    )

    request = RecommendationRequest(
        userId="550e8400-e29b-41d4-a716-446655440004",
        riskProfile="Low",
        investmentAmount=20000,
        investmentHorizon=2
    )

    result = recommendation_service.recommend_funds(request)

    assert "recommendedFunds" in result
    assert len(result["recommendedFunds"]) == 3

    # No risk match, highest return should win
    assert (
        result["recommendedFunds"][0]["fundName"]
        == "Nippon India Small Cap Fund"
    )

    assert result["recommendedFunds"][0]["score"] == 12