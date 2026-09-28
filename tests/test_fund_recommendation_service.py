from __future__ import annotations

from unittest.mock import Mock

import pytest

from app.schemas.fund_recommendation import (
    FundRecommendationResponse,
)
from app.services.fund_recommendation_scoring_service import (
    FundRecommendationScoringConfig,
)
from app.services.fund_recommendation_service import (
    FundRecommendationService,
)


@pytest.fixture
def scoring_config():
    return FundRecommendationScoringConfig(
        return_weight=0.35,
        cost_weight=0.20,
        size_weight=0.45,
        return_lower_bound=-20.0,
        return_upper_bound=30.0,
        expense_ratio_lower_bound=0.0,
        expense_ratio_upper_bound=2.0,
        unknown_cost_score=0.5,
        unknown_size_score=0.5,
        size_log_divisor=4.0,
        strong_return_threshold=0.60,
        low_cost_threshold=0.60,
    )


@pytest.fixture
def repositories():
    return {
        "fund": Mock(),
        "profile": Mock(),
        "exposure": Mock(),
    }


@pytest.fixture
def services():
    return {
        "scoring": Mock(),
        "collaborative": Mock(),
        "diversity": Mock(),
        "trending": Mock(),
    }


@pytest.fixture
def recommendation_service(
    repositories,
    services,
):
    return FundRecommendationService(
        fund_repository=repositories["fund"],
        profile_repository=repositories["profile"],
        exposure_repository=repositories["exposure"],
        scoring_service=services["scoring"],
        collaborative_service=services["collaborative"],
        diversity_service=services["diversity"],
        trending_service=services["trending"],
    )


def _configure_profile(
    repositories,
    *,
    user_id="user-1",
    level=3,
):
    repositories["profile"].get_profile.return_value = {
        "user_id": user_id,
        "level": level,
    }


def _configure_fund(repositories):
    repositories["fund"].get_active_funds.return_value = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Test Fund",
            "amc_name": "Test AMC",
            "category": "Equity",
        }
    ]


def _configure_scoring(services):
    services["scoring"].score_funds.return_value = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Test Fund",
            "amc_name": "Test AMC",
            "category": "Equity",
            "score": 0.85,
            "explanation": "Strong return and cost profile.",
        }
    ]


def _configure_diversity(services):
    services["diversity"].select_diverse_funds.return_value = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Test Fund",
            "amc_name": "Test AMC",
            "category": "Equity",
            "score": 0.85,
            "explanation": "Strong return and cost profile.",
        }
    ]


def _configure_collaborative(
    services,
    *,
    available=False,
):
    services[
        "collaborative"
    ].calculate_signal.return_value = {
        "available": available,
    }


def _configure_trending(services):
    services["trending"].get_trending.return_value = [
        {
            "schemeCode": "TREND001",
            "schemeName": "Trending Fund",
            "amcName": "Trending AMC",
            "learnerLevel": "3",
            "exposureCount": 5,
        }
    ]


def test_empty_catalog_returns_empty_recommendations(
    recommendation_service,
    repositories,
):
    _configure_profile(repositories)

    repositories["fund"].get_active_funds.return_value = []

    result = recommendation_service.recommend(
        user_id="user-1",
    )

    assert isinstance(
        result,
        FundRecommendationResponse,
    )
    assert result.userId == "user-1"
    assert result.recommendations == []
    assert result.trendingAmongLearners == []


def test_recommendations_are_generated(
    recommendation_service,
    repositories,
    services,
):
    _configure_profile(repositories)
    _configure_fund(repositories)
    _configure_scoring(services)
    _configure_diversity(services)
    _configure_collaborative(services)
    _configure_trending(services)

    repositories[
        "exposure"
    ].get_recent_user_exposures.return_value = []

    result = recommendation_service.recommend(
        user_id="user-1",
    )

    assert result.userId == "user-1"
    assert len(result.recommendations) == 1

    recommendation = result.recommendations[0]

    assert recommendation.schemeCode == "FUND001"
    assert recommendation.schemeName == "Test Fund"
    assert recommendation.amcName == "Test AMC"
    assert recommendation.category == "Equity"
    assert recommendation.score == 0.85
    assert (
        recommendation.explanation
        == "Strong return and cost profile."
    )
    assert recommendation.collaborativeAvailable is False


def test_recommendations_record_exposure(
    recommendation_service,
    repositories,
    services,
):
    _configure_profile(repositories)
    _configure_fund(repositories)
    _configure_scoring(services)
    _configure_diversity(services)
    _configure_collaborative(services)
    _configure_trending(services)

    repositories[
        "exposure"
    ].get_recent_user_exposures.return_value = []

    recommendation_service.recommend(
        user_id="user-1",
    )

    repositories[
        "exposure"
    ].record_exposure.assert_called_once_with(
        user_id="user-1",
        scheme_code="FUND001",
        amc_name="Test AMC",
        recommendation_rank=1,
        recommendation_source="HYBRID",
    )


def test_goal_and_level_are_forwarded(
    recommendation_service,
    repositories,
    services,
):
    _configure_profile(
        repositories,
        level=2,
    )
    _configure_fund(repositories)
    _configure_scoring(services)
    _configure_diversity(services)
    _configure_collaborative(services)
    _configure_trending(services)

    repositories[
        "exposure"
    ].get_recent_user_exposures.return_value = []

    recommendation_service.recommend(
        user_id="user-1",
        goal="retirement",
        level="4",
    )

    services[
        "scoring"
    ].score_funds.assert_called_once_with(
        repositories["fund"].get_active_funds.return_value,
        goal="retirement",
        level="4",
    )

    services[
        "trending"
    ].get_trending.assert_called_once_with(
        level=4,
        days=28,
        limit=5,
    )


def test_collaborative_signal_is_unavailable_without_peer_data(
    recommendation_service,
    repositories,
    services,
):
    _configure_profile(repositories)
    _configure_fund(repositories)
    _configure_scoring(services)
    _configure_diversity(services)
    _configure_collaborative(
        services,
        available=False,
    )
    _configure_trending(services)

    repositories[
        "exposure"
    ].get_recent_user_exposures.return_value = []

    result = recommendation_service.recommend(
        user_id="user-1",
    )

    recommendation = result.recommendations[0]

    assert recommendation.collaborativeAvailable is False

    assert (
        "Users with similar activity"
        not in recommendation.explanation
    )


def test_collaborative_signal_is_included_when_available(
    recommendation_service,
    repositories,
    services,
):
    _configure_profile(repositories)
    _configure_fund(repositories)
    _configure_scoring(services)
    _configure_diversity(services)
    _configure_collaborative(
        services,
        available=True,
    )
    _configure_trending(services)

    repositories[
        "exposure"
    ].get_recent_user_exposures.return_value = []

    result = recommendation_service.recommend(
        user_id="user-1",
    )

    recommendation = result.recommendations[0]

    assert recommendation.collaborativeAvailable is True

    assert (
        "Users with similar activity also considered this fund."
        in recommendation.explanation
    )


def test_trending_funds_are_returned(
    recommendation_service,
    repositories,
    services,
):
    _configure_profile(repositories)
    _configure_fund(repositories)
    _configure_scoring(services)
    _configure_diversity(services)
    _configure_collaborative(services)
    _configure_trending(services)

    repositories[
        "exposure"
    ].get_recent_user_exposures.return_value = []

    result = recommendation_service.recommend(
        user_id="user-1",
    )

    assert len(result.trendingAmongLearners) == 1

    trending = result.trendingAmongLearners[0]

    assert trending.schemeCode == "TREND001"
    assert trending.schemeName == "Trending Fund"
    assert trending.amcName == "Trending AMC"
    assert trending.learnerLevel == "3"
    assert trending.exposureCount == 5


def test_missing_profile_raises_error(
    recommendation_service,
    repositories,
):
    repositories[
        "profile"
    ].get_profile.return_value = None

    with pytest.raises(
        ValueError,
        match="Profile not found for user: user-1",
    ):
        recommendation_service.recommend(
            user_id="user-1",
        )


def test_invalid_user_id_raises_error(
    recommendation_service,
):
    with pytest.raises(
        ValueError,
        match="user_id cannot be empty",
    ):
        recommendation_service.recommend(
            user_id="   ",
        )


def test_invalid_limit_raises_error(
    recommendation_service,
    repositories,
):
    _configure_profile(repositories)

    with pytest.raises(
        ValueError,
        match="limit must be greater than zero",
    ):
        recommendation_service.recommend(
            user_id="user-1",
            limit=0,
        )