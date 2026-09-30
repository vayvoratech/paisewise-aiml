from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.fund_recommendation import (
    FundRecommendationResponse,
)


def test_fund_recommendation_route():
    mock_response = FundRecommendationResponse(
        userId="user-1",
        recommendations=[],
        trendingAmongLearners=[],
    )

    mock_service = MagicMock()
    mock_service.recommend.return_value = mock_response

    with patch(
        "app.api.routes.fund_recommendation."
        "FundRecommendationService",
        return_value=mock_service,
    ):
        client = TestClient(app)

        response = client.post(
            "/ai/fund-recommendations",
            json={
                "userId": "user-1",
                "context": {
                    "goal": "retirement",
                    "level": "2",
                },
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert body["userId"] == "user-1"
    assert body["recommendations"] == []
    assert body["trendingAmongLearners"] == []

    mock_service.recommend.assert_called_once_with(
        user_id="user-1",
        goal="retirement",
        level="2",
    )


def test_fund_recommendation_route_accepts_no_context():
    mock_response = FundRecommendationResponse(
        userId="user-1",
        recommendations=[],
        trendingAmongLearners=[],
    )

    mock_service = MagicMock()
    mock_service.recommend.return_value = mock_response

    with patch(
        "app.api.routes.fund_recommendation."
        "FundRecommendationService",
        return_value=mock_service,
    ):
        client = TestClient(app)

        response = client.post(
            "/ai/fund-recommendations",
            json={
                "userId": "user-1",
            },
        )

    assert response.status_code == 200

    mock_service.recommend.assert_called_once_with(
        user_id="user-1",
        goal=None,
        level=None,
    )