from pydantic import ValidationError
import pytest

from app.schemas.fund_recommendation import (
    FundRecommendationContext,
    FundRecommendationRequest,
    FundRecommendationResponse,
)


def test_request_accepts_user_id_without_context():
    request = FundRecommendationRequest(userId="user-1")

    assert request.userId == "user-1"
    assert request.context is None


def test_request_accepts_optional_context():
    request = FundRecommendationRequest(
        userId="user-1",
        context=FundRecommendationContext(
            goal="retirement",
            level="2",
        ),
    )

    assert request.context is not None
    assert request.context.goal == "retirement"
    assert request.context.level == "2"


def test_request_rejects_empty_user_id():
    with pytest.raises(ValidationError):
        FundRecommendationRequest(userId="")


def test_response_defaults_to_empty_lists():
    response = FundRecommendationResponse(
        userId="user-1",
    )

    assert response.recommendations == []
    assert response.trendingAmongLearners == []