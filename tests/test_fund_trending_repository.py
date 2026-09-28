from unittest.mock import MagicMock, patch

import pytest

from app.repositories.fund_trending_repository import (
    FundTrendingRepository,
)


def _description(name: str) -> MagicMock:
    item = MagicMock()
    item.name = name
    return item


def test_rejects_invalid_level():
    repository = FundTrendingRepository()

    with pytest.raises(ValueError, match="level"):
        repository.get_trending_for_level(0)


def test_rejects_invalid_days():
    repository = FundTrendingRepository()

    with pytest.raises(ValueError, match="days"):
        repository.get_trending_for_level(
            1,
            days=0,
        )


def test_rejects_invalid_limit():
    repository = FundTrendingRepository()

    with pytest.raises(ValueError, match="limit"):
        repository.get_trending_for_level(
            1,
            limit=0,
        )


@patch(
    "app.repositories.fund_trending_repository.get_db"
)
def test_returns_trending_funds(mock_get_db):
    cursor = MagicMock()

    cursor.description = [
        _description("scheme_code"),
        _description("scheme_name"),
        _description("amc_name"),
        _description("exposure_count"),
        _description("unique_user_count"),
    ]

    cursor.fetchall.return_value = [
        (
            "FUND001",
            "Example Growth Fund",
            "Example AMC",
            12,
            5,
        )
    ]

    connection = MagicMock()

    connection.cursor.return_value.__enter__.return_value = (
        cursor
    )

    mock_get_db.return_value.__enter__.return_value = (
        connection
    )

    repository = FundTrendingRepository()

    result = repository.get_trending_for_level(
        2,
        days=28,
        limit=10,
    )

    assert len(result) == 1

    assert result[0]["scheme_code"] == "FUND001"
    assert (
        result[0]["scheme_name"]
        == "Example Growth Fund"
    )
    assert result[0]["amc_name"] == "Example AMC"
    assert result[0]["exposure_count"] == 12
    assert result[0]["unique_user_count"] == 5

    cursor.execute.assert_called_once()


@patch(
    "app.repositories.fund_trending_repository.get_db"
)
def test_returns_empty_when_no_trending_funds(
    mock_get_db,
):
    cursor = MagicMock()

    cursor.description = [
        _description("scheme_code"),
        _description("scheme_name"),
        _description("amc_name"),
        _description("exposure_count"),
        _description("unique_user_count"),
    ]

    cursor.fetchall.return_value = []

    connection = MagicMock()

    connection.cursor.return_value.__enter__.return_value = (
        cursor
    )

    mock_get_db.return_value.__enter__.return_value = (
        connection
    )

    repository = FundTrendingRepository()

    result = repository.get_trending_for_level(
        2,
    )

    assert result == []