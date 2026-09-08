import time
from models.recommendation import RecommendationRequest
from services import recommendation_service


def test_recommendation_performance(monkeypatch):

    # Mock external/database-dependent operations
    monkeypatch.setattr(
        recommendation_service,
        "get_catalogue",
        lambda: [
            {
                "scheme_code": "AXIS001",
                "scheme_name": "Axis Bluechip Fund",
                "risk_level": "Moderate",
                "return_1y": 12.5,
                "expense_ratio": 0.5,
                "aum_crore": 50000
            },
            {
                "scheme_code": "PARAG001",
                "scheme_name": "Parag Parikh Flexi Cap Fund",
                "risk_level": "Moderate",
                "return_1y": 14.2,
                "expense_ratio": 0.4,
                "aum_crore": 60000
            },
            {
                "scheme_code": "NIPPON001",
                "scheme_name": "Nippon India Small Cap Fund",
                "risk_level": "High",
                "return_1y": 18.5,
                "expense_ratio": 0.6,
                "aum_crore": 70000
            }
        ]
    )

    monkeypatch.setattr(
        recommendation_service,
        "generate_fund_explanation",
        lambda fund, risk_profile: "Test explanation"
    )

    monkeypatch.setattr(
        recommendation_service,
        "assign_recommendation_variant",
        lambda user_id: "A"
    )

    monkeypatch.setattr(
        recommendation_service,
        "create_recommendation_run",
        lambda user_id, variant: "test-run-id"
    )

    # Force cache miss so we measure recommendation calculation
    monkeypatch.setattr(
        recommendation_service,
        "get_cached_recommendation",
        lambda user_id: None
    )

    monkeypatch.setattr(
        recommendation_service,
        "cache_recommendation",
        lambda user_id, result: None
    )

    request = RecommendationRequest(
        userId="11111111-1111-1111-1111-111111111111",
        riskProfile="Moderate",
        investmentAmount=50000,
        investmentHorizon=3
    )

    start_time = time.perf_counter()

    recommendation_service.recommend_funds(request)

    elapsed_time = time.perf_counter() - start_time

    elapsed_ms = elapsed_time * 1000

    print(f"\nRecommendation calculation time: {elapsed_ms:.2f} ms")

    assert elapsed_ms < 500, (
        f"Recommendation calculation took {elapsed_ms:.2f} ms, "
        "which exceeds the 500 ms requirement"
    )