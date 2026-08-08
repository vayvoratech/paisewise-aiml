import json
from pathlib import Path

from models.recommendation import RecommendationRequest
from services import recommendation_service


BASELINE_FILE = Path(
    "tests/recommendation_baseline.json"
)


def test_recommendation_regression(monkeypatch):

    # Load old approved recommendation
    with open(BASELINE_FILE) as file:
        baseline = json.load(file)


    profile = baseline["moderate_user_profile"]


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
        userId=profile["userId"],
        riskProfile=profile["riskProfile"],
        investmentAmount=profile["investmentAmount"],
        investmentHorizon=profile["investmentHorizon"]
    )


    # Get new recommendation
    result = recommendation_service.recommend_funds(request)


    new_funds = [
        fund["fundName"]
        for fund in result["recommendedFunds"]
    ]


    old_funds = profile["recommendedFunds"]


    # Find common funds
    common_funds = set(old_funds) & set(new_funds)


    similarity = len(common_funds) / len(old_funds)


    assert similarity >= 0.5, (
        "Recommendation changed significantly. "
        "Review required."
    )