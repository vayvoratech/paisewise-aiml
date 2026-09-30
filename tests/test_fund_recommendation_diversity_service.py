import pytest

from app.services.fund_recommendation_diversity_service import (
    FundRecommendationDiversityService,
)


def _candidate(
    scheme_code: str,
    score: float,
) -> dict:
    return {
        "scheme_code": scheme_code,
        "scheme_name": f"Fund {scheme_code}",
        "amc_name": "Example AMC",
        "category": "Equity",
        "score": score,
    }


def test_empty_candidates_returns_empty_list():
    service = FundRecommendationDiversityService()

    result = service.select_diverse_funds(
        [],
        [],
    )

    assert result == []


def test_prefers_funds_not_recently_exposed():
    service = FundRecommendationDiversityService()

    candidates = [
        _candidate("FUND001", 0.95),
        _candidate("FUND002", 0.90),
        _candidate("FUND003", 0.85),
    ]

    exposures = [
        {"scheme_code": "FUND001"},
    ]

    result = service.select_diverse_funds(
        candidates,
        exposures,
        limit=2,
    )

    assert [
        item["scheme_code"]
        for item in result
    ] == [
        "FUND002",
        "FUND003",
    ]


def test_falls_back_to_exposed_fund_when_needed():
    service = FundRecommendationDiversityService()

    candidates = [
        _candidate("FUND001", 0.95),
        _candidate("FUND002", 0.90),
    ]

    exposures = [
        {"scheme_code": "FUND001"},
        {"scheme_code": "FUND002"},
    ]

    result = service.select_diverse_funds(
        candidates,
        exposures,
        limit=2,
    )

    assert len(result) == 2


def test_does_not_return_duplicate_funds():
    service = FundRecommendationDiversityService()

    candidates = [
        _candidate("FUND001", 0.95),
        _candidate("FUND001", 0.90),
        _candidate("FUND002", 0.85),
    ]

    result = service.select_diverse_funds(
        candidates,
        [],
        limit=3,
    )

    assert [
        item["scheme_code"]
        for item in result
    ] == [
        "FUND001",
        "FUND002",
    ]


def test_respects_limit():
    service = FundRecommendationDiversityService()

    candidates = [
        _candidate("FUND001", 0.95),
        _candidate("FUND002", 0.90),
        _candidate("FUND003", 0.85),
        _candidate("FUND004", 0.80),
    ]

    result = service.select_diverse_funds(
        candidates,
        [],
        limit=2,
    )

    assert len(result) == 2


def test_rejects_invalid_limit():
    service = FundRecommendationDiversityService()

    with pytest.raises(
        ValueError,
        match="limit",
    ):
        service.select_diverse_funds(
            [_candidate("FUND001", 0.95)],
            [],
            limit=0,
        )


def test_rejects_candidate_without_scheme_code():
    service = FundRecommendationDiversityService()

    candidate = _candidate("FUND001", 0.95)
    candidate["scheme_code"] = ""

    with pytest.raises(
        ValueError,
        match="scheme_code",
    ):
        service.select_diverse_funds(
            [candidate],
            [],
        )