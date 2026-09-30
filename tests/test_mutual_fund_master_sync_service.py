from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch
from app.services.amfi_scheme_details_provider import (
    AMFISchemeDetailsProvider,
)
from app.services.mutual_fund_master_sync_service import (
    MutualFundMasterSyncService,
)


def _record(
    *,
    scheme_code="100001",
    scheme_name="Sample Fund",
    isin="INF000000001",
    amc_name="Sample AMC",
    category="Equity",
    sub_category="Large Cap",
    scheme_type="Open Ended",
    min_sip_amount=Decimal("100"),
    min_lumpsum=Decimal("1000"),
    returns_1y=Decimal("10.50"),
    returns_3y=Decimal("12.25"),
    returns_5y=Decimal("14.10"),
    expense_ratio=Decimal("1.20"),
    fund_manager="Sample Manager",
    fund_size_cr=Decimal("5000"),
    is_tax_saver=False,
    lock_in_years=None,
):
    return AMFISchemeDetailsProvider.normalize(
        scheme_code=scheme_code,
        scheme_name=scheme_name,
        isin=isin,
        amc_name=amc_name,
        category=category,
        sub_category=sub_category,
        scheme_type=scheme_type,
        min_sip_amount=min_sip_amount,
        min_lumpsum=min_lumpsum,
        returns_1y=returns_1y,
        returns_3y=returns_3y,
        returns_5y=returns_5y,
        expense_ratio=expense_ratio,
        fund_manager=fund_manager,
        fund_size_cr=fund_size_cr,
        is_tax_saver=is_tax_saver,
        lock_in_years=lock_in_years,
    )


def _invalid_record():
    """
    Create a deliberately invalid record without going
    through AMFISchemeDetailsProvider.normalize(), because
    normalize() correctly rejects an empty scheme_code.
    """
    record = Mock()

    record.scheme_code = ""
    record.scheme_name = "Invalid Fund"
    record.amc_name = "Sample AMC"
    record.scheme_type = "Open Ended"

    return record


def _mock_db():
    """
    Create a database context-manager mock.

    get_db() returns a context manager whose __enter__()
    returns the database connection.

    connection.cursor() also returns a context manager whose
    __enter__() returns the cursor.
    """
    connection = MagicMock()
    cursor = MagicMock()

    cursor_context = MagicMock()
    cursor_context.__enter__.return_value = cursor
    cursor_context.__exit__.return_value = None

    connection.cursor.return_value = cursor_context

    db_context = MagicMock()
    db_context.__enter__.return_value = connection
    db_context.__exit__.return_value = None

    return db_context, connection, cursor


def test_empty_records_return_zero_counts():
    service = MutualFundMasterSyncService()

    result = service.sync([])

    assert result == {
        "processed": 0,
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
    }


def test_invalid_record_is_skipped():
    service = MutualFundMasterSyncService()

    invalid_record = _invalid_record()

    result = service.sync([invalid_record])

    assert result["processed"] == 1
    assert result["inserted"] == 0
    assert result["updated"] == 0
    assert result["skipped"] == 1


def test_new_record_is_inserted_without_risk_level():
    service = MutualFundMasterSyncService()

    record = _record(
        scheme_code="100001",
    )

    db_context, connection, cursor = _mock_db()

    cursor.fetchone.return_value = None
    cursor.rowcount = 1

    with patch(
        "app.services.mutual_fund_master_sync_service.get_db",
        return_value=db_context,
    ):
        result = service.sync([record])

    assert result["processed"] == 1
    assert result["inserted"] == 1
    assert result["updated"] == 0
    assert result["skipped"] == 0

    assert cursor.execute.call_count == 2

    insert_call = cursor.execute.call_args_list[1]

    sql = insert_call.args[0]

    assert "INSERT INTO mf_schemes" in sql
    assert "risk_level" not in sql

    connection.commit.assert_called_once()


def test_existing_record_is_updated_without_risk_level():
    service = MutualFundMasterSyncService()

    record = _record(
        scheme_code="100001",
    )

    db_context, connection, cursor = _mock_db()

    cursor.fetchone.return_value = (
        "100001",
    )
    cursor.rowcount = 1

    with patch(
        "app.services.mutual_fund_master_sync_service.get_db",
        return_value=db_context,
    ):
        result = service.sync([record])

    assert result["processed"] == 1
    assert result["inserted"] == 0
    assert result["updated"] == 1
    assert result["skipped"] == 0

    assert cursor.execute.call_count == 2

    update_call = cursor.execute.call_args_list[1]

    sql = update_call.args[0]

    assert "UPDATE mf_schemes" in sql
    assert "risk_level" not in sql

    connection.commit.assert_called_once()


def test_existing_non_null_values_are_preserved_when_source_values_are_none():
    service = MutualFundMasterSyncService()

    record = _record(
        scheme_code="100001",
        isin=None,
        category=None,
        sub_category=None,
        min_sip_amount=None,
        min_lumpsum=None,
        returns_1y=None,
        returns_3y=None,
        returns_5y=None,
        expense_ratio=None,
        fund_manager=None,
        fund_size_cr=None,
        lock_in_years=None,
    )

    db_context, connection, cursor = _mock_db()

    cursor.fetchone.return_value = (
        "100001",
    )
    cursor.rowcount = 1

    with patch(
        "app.services.mutual_fund_master_sync_service.get_db",
        return_value=db_context,
    ):
        result = service.sync([record])

    assert result["processed"] == 1
    assert result["updated"] == 1
    assert result["skipped"] == 0

    update_call = cursor.execute.call_args_list[1]

    sql = update_call.args[0]
    params = update_call.args[1]

    assert "COALESCE" in sql
    assert "risk_level" not in sql

    assert params[1] is None
    assert params[3] is None
    assert params[4] is None
    assert params[6] is None


def test_multiple_records_are_processed():
    service = MutualFundMasterSyncService()

    records = [
        _record(
            scheme_code="100001",
            scheme_name="Fund One",
        ),
        _record(
            scheme_code="100002",
            scheme_name="Fund Two",
        ),
    ]

    db_context, connection, cursor = _mock_db()

    cursor.fetchone.side_effect = [
        None,
        None,
    ]
    cursor.rowcount = 1

    with patch(
        "app.services.mutual_fund_master_sync_service.get_db",
        return_value=db_context,
    ):
        result = service.sync(records)

    assert result["processed"] == 2
    assert result["inserted"] == 2
    assert result["updated"] == 0
    assert result["skipped"] == 0

    connection.commit.assert_called_once()


def test_invalid_records_are_skipped_while_valid_records_continue():
    service = MutualFundMasterSyncService()

    invalid_record = _invalid_record()

    valid_record = _record(
        scheme_code="100002",
    )

    db_context, connection, cursor = _mock_db()

    cursor.fetchone.return_value = None
    cursor.rowcount = 1

    with patch(
        "app.services.mutual_fund_master_sync_service.get_db",
        return_value=db_context,
    ):
        result = service.sync(
            [
                invalid_record,
                valid_record,
            ]
        )

    assert result["processed"] == 2
    assert result["inserted"] == 1
    assert result["updated"] == 0
    assert result["skipped"] == 1

    connection.commit.assert_called_once()


def test_sync_commits_transaction():
    service = MutualFundMasterSyncService()

    record = _record()

    db_context, connection, cursor = _mock_db()

    cursor.fetchone.return_value = None
    cursor.rowcount = 1

    with patch(
        "app.services.mutual_fund_master_sync_service.get_db",
        return_value=db_context,
    ):
        service.sync([record])

    connection.commit.assert_called_once()