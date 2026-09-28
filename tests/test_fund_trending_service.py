from unittest.mock import MagicMock

import pytest

from app.services.fund_trending_service import (
    FundTrendingService,
)


def test_rejects_invalid_level():
    repository = MagicMock()
    service = FundTrendingService(repository)

    with pytest.raises(
        ValueError,
        match="level",
    ):
        service.get_trending(level=0)


def test_rejects_invalid_days():
    repository = MagicMock()
    service = FundTrendingService(repository)

    with pytest.raises(
        ValueError,
        match="days",
    ):
        service.get_trending(
            level=2,
            days=0,
        )


def test_rejects_invalid_limit():
    repository = MagicMock()
    service = FundTrendingService(repository)

    with pytest.raises(
        ValueError,
        match="limit",
    ):
        service.get_trending(
            level=2,
            limit=0,
        )


def test_returns_trending_funds():
    repository = MagicMock()

    repository.get_trending_for_level.return_value = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Example Growth Fund",
            "amc_name": "Example AMC",
            "exposure_count": 12,
            "unique_user_count": 5,
        }
    ]

    service = FundTrendingService(repository)

    result = service.get_trending(
        level=2,
        days=28,
        limit=5,
    )

    assert result == [
        {
            "schemeCode": "FUND001",
            "schemeName": "Example Growth Fund",
            "amcName": "Example AMC",
            "learnerLevel": "2",
            "exposureCount": 12,
        }
    ]

    repository.get_trending_for_level.assert_called_once_with(
        2,
        days=28,
        limit=5,
    )


def test_returns_empty_when_no_real_data():
    repository = MagicMock()
    repository.get_trending_for_level.return_value = []

    service = FundTrendingService(repository)

    result = service.get_trending(
        level=2,
    )

    assert result == []


def test_exposure_count_is_integer():
    repository = MagicMock()

    repository.get_trending_for_level.return_value = [
        {
            "scheme_code": "FUND001",
            "scheme_name": "Example Fund",
            "amc_name": "Example AMC",
            "exposure_count": "7",
            "unique_user_count": "3",
        }
    ]

    service = FundTrendingService(repository)

    result = service.get_trending(level=2)

    assert result[0]["exposureCount"] == 7
    assert isinstance(
        result[0]["exposureCount"],
        int,
    )