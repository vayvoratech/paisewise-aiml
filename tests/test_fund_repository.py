from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.repositories.fund_repository import FundRepository


COLUMNS = [
    "scheme_code",
    "isin",
    "scheme_name",
    "amc_name",
    "amc_code",
    "category",
    "sub_category",
    "scheme_type",
    "risk_level",
    "nav",
    "nav_date",
    "min_sip_amount",
    "min_lumpsum",
    "sip_multiplier",
    "returns_1y",
    "returns_3y",
    "returns_5y",
    "returns_since_launch",
    "benchmark_name",
    "benchmark_returns_1y",
    "expense_ratio",
    "fund_manager",
    "fund_size_cr",
    "launch_date",
    "is_active",
    "is_tax_saver",
    "lock_in_years",
    "dividend_option",
    "growth_option",
    "bse_scheme_code",
    "nse_symbol",
    "updated_at",
]


FUND_ROW = (
    "INF0001",
    "INE000000001",
    "Test Growth Fund",
    "Test AMC",
    "AMC001",
    "Equity",
    "Large Cap",
    "Open Ended",
    "High",
    100.25,
    None,
    500.00,
    1000.00,
    1.00,
    12.50,
    15.20,
    14.80,
    10.10,
    "NIFTY 50",
    11.20,
    0.0125,
    "Test Manager",
    5000.00,
    None,
    True,
    False,
    0,
    False,
    True,
    "BSE001",
    "TEST",
    None,
)


@pytest.fixture
def repository():
    return FundRepository()


@pytest.fixture
def mock_db():
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    cursor.description = [
        SimpleNamespace(name=column)
        for column in COLUMNS
    ]

    return connection, cursor


def test_get_active_funds_returns_rows(repository, mock_db):
    connection, cursor = mock_db

    cursor.fetchall.return_value = [FUND_ROW]

    with patch(
        "app.repositories.fund_repository.get_db",
        return_value=connection,
    ):
        result = repository.get_active_funds()

    assert len(result) == 1
    assert result[0]["scheme_code"] == "INF0001"
    assert result[0]["scheme_name"] == "Test Growth Fund"
    assert result[0]["amc_name"] == "Test AMC"

    query = cursor.execute.call_args[0][0]

    assert "FROM mf_schemes" in query
    assert "is_active = TRUE" in query
    assert "investment.funds" not in query
    assert "learning_level" not in query
    assert "management_style" not in query


def test_get_active_funds_by_category(repository, mock_db):
    connection, cursor = mock_db

    cursor.fetchall.return_value = []

    with patch(
        "app.repositories.fund_repository.get_db",
        return_value=connection,
    ):
        result = repository.get_active_funds_by_category("Equity")

    assert result == []

    cursor.execute.assert_called_once()

    query, params = cursor.execute.call_args[0]

    assert "FROM mf_schemes" in query
    assert "category = %s" in query
    assert params == ("Equity",)


def test_get_active_funds_by_category_rejects_empty_category(repository):
    with pytest.raises(ValueError, match="category cannot be empty"):
        repository.get_active_funds_by_category("")


def test_get_active_funds_by_category_rejects_whitespace_category(repository):
    with pytest.raises(ValueError, match="category cannot be empty"):
        repository.get_active_funds_by_category("   ")


def test_get_active_funds_by_amc(repository, mock_db):
    connection, cursor = mock_db

    cursor.fetchall.return_value = []

    with patch(
        "app.repositories.fund_repository.get_db",
        return_value=connection,
    ):
        result = repository.get_active_funds_by_amc("Test AMC")

    assert result == []

    cursor.execute.assert_called_once()

    query, params = cursor.execute.call_args[0]

    assert "FROM mf_schemes" in query
    assert "amc_name = %s" in query
    assert params == ("Test AMC",)


def test_get_active_funds_by_amc_rejects_empty_amc(repository):
    with pytest.raises(ValueError, match="amc_name cannot be empty"):
        repository.get_active_funds_by_amc("")


def test_get_active_funds_by_amc_rejects_whitespace_amc(repository):
    with pytest.raises(ValueError, match="amc_name cannot be empty"):
        repository.get_active_funds_by_amc("   ")


def test_get_by_scheme_code_returns_fund(repository, mock_db):
    connection, cursor = mock_db

    cursor.fetchone.return_value = FUND_ROW

    with patch(
        "app.repositories.fund_repository.get_db",
        return_value=connection,
    ):
        result = repository.get_by_scheme_code("INF0001")

    assert result is not None
    assert result["scheme_code"] == "INF0001"
    assert result["scheme_name"] == "Test Growth Fund"

    query, params = cursor.execute.call_args[0]

    assert "FROM mf_schemes" in query
    assert "scheme_code = %s" in query
    assert params == ("INF0001",)


def test_get_by_scheme_code_returns_none_when_not_found(
    repository,
    mock_db,
):
    connection, cursor = mock_db

    cursor.fetchone.return_value = None

    with patch(
        "app.repositories.fund_repository.get_db",
        return_value=connection,
    ):
        result = repository.get_by_scheme_code("UNKNOWN")

    assert result is None


def test_get_by_scheme_code_rejects_empty_code(repository):
    with pytest.raises(ValueError, match="scheme_code cannot be empty"):
        repository.get_by_scheme_code("")


def test_get_by_scheme_code_rejects_whitespace_code(repository):
    with pytest.raises(ValueError, match="scheme_code cannot be empty"):
        repository.get_by_scheme_code("   ")