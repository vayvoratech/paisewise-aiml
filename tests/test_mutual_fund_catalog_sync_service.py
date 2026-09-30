from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.amfi_nav_provider import AMFINAVRecord
from app.services.mutual_fund_catalog_sync_service import (
    MutualFundCatalogSyncService,
)


def make_record(
    scheme_code: str = "100001",
    scheme_name: str = "Sample Equity Fund",
    isin_growth: str | None = "INF000000001",
    isin_div_reinvestment: str | None = None,
    nav: str = "125.4567",
) -> AMFINAVRecord:
    return AMFINAVRecord(
        scheme_code=scheme_code,
        scheme_name=scheme_name,
        isin_growth=isin_growth,
        isin_div_reinvestment=isin_div_reinvestment,
        nav=Decimal(nav),
        nav_date=date(2026, 9, 21),
    )


def create_db_mock(existing_scheme_codes: set[str]):
    connection = MagicMock()
    cursor = MagicMock()

    def fetchone_side_effect():
        return cursor._current_result

    cursor.fetchone.side_effect = fetchone_side_effect

    def execute_side_effect(sql, params=None):
        normalized_sql = " ".join(sql.split())

        if normalized_sql.startswith(
            "SELECT scheme_code FROM mf_schemes"
        ):
            scheme_code = params[0]
            cursor._current_result = (
                (scheme_code,)
                if scheme_code in existing_scheme_codes
                else None
            )
            return

        if normalized_sql.startswith("UPDATE mf_schemes"):
            cursor.rowcount = 1
            return

    cursor.execute.side_effect = execute_side_effect

    connection.cursor.return_value.__enter__.return_value = cursor
    connection.cursor.return_value.__exit__.return_value = False

    return connection, cursor


@patch(
    "app.services.mutual_fund_catalog_sync_service.get_db"
)
def test_existing_scheme_is_updated(mock_get_db):
    connection, cursor = create_db_mock({"100001"})
    mock_get_db.return_value.__enter__.return_value = connection
    mock_get_db.return_value.__exit__.return_value = False

    service = MutualFundCatalogSyncService()

    result = service.sync([make_record()])

    assert result == {
        "processed": 1,
        "updated": 1,
        "skipped": 0,
    }

    assert cursor.execute.call_count == 2

    update_call = cursor.execute.call_args_list[1]

    assert "UPDATE mf_schemes" in update_call.args[0]
    assert update_call.args[1] == (
        "INF000000001",
        Decimal("125.4567"),
        date(2026, 9, 21),
        "100001",
    )

    connection.commit.assert_called_once()


@patch(
    "app.services.mutual_fund_catalog_sync_service.get_db"
)
def test_unknown_scheme_is_skipped(mock_get_db):
    connection, cursor = create_db_mock(set())
    mock_get_db.return_value.__enter__.return_value = connection
    mock_get_db.return_value.__exit__.return_value = False

    service = MutualFundCatalogSyncService()

    result = service.sync([make_record(scheme_code="999999")])

    assert result == {
        "processed": 1,
        "updated": 0,
        "skipped": 1,
    }

    assert cursor.execute.call_count == 1

    connection.commit.assert_called_once()


@patch(
    "app.services.mutual_fund_catalog_sync_service.get_db"
)
def test_multiple_records_are_processed(mock_get_db):
    connection, cursor = create_db_mock(
        {
            "100001",
            "100002",
        }
    )

    mock_get_db.return_value.__enter__.return_value = connection
    mock_get_db.return_value.__exit__.return_value = False

    records = [
        make_record(scheme_code="100001"),
        make_record(scheme_code="100002"),
        make_record(scheme_code="100003"),
    ]

    service = MutualFundCatalogSyncService()

    result = service.sync(records)

    assert result == {
        "processed": 3,
        "updated": 2,
        "skipped": 1,
    }

    connection.commit.assert_called_once()


@patch(
    "app.services.mutual_fund_catalog_sync_service.get_db"
)
def test_empty_records_do_not_touch_database(mock_get_db):
    service = MutualFundCatalogSyncService()

    result = service.sync([])

    assert result == {
        "processed": 0,
        "updated": 0,
        "skipped": 0,
    }

    mock_get_db.assert_not_called()


@patch(
    "app.services.mutual_fund_catalog_sync_service.get_db"
)
def test_missing_isin_does_not_overwrite_existing_isin(mock_get_db):
    connection, cursor = create_db_mock({"100001"})

    mock_get_db.return_value.__enter__.return_value = connection
    mock_get_db.return_value.__exit__.return_value = False

    record = make_record(isin_growth=None)

    service = MutualFundCatalogSyncService()

    result = service.sync([record])

    assert result["updated"] == 1

    update_call = cursor.execute.call_args_list[1]

    assert update_call.args[1][0] is None

    connection.commit.assert_called_once()