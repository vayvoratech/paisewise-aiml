from decimal import Decimal

from app.db.session import get_db
from app.services.amfi_scheme_details_provider import (
    AMFISchemeDetailsProvider,
)
from app.services.mutual_fund_master_sync_service import (
    MutualFundMasterSyncService,
)


TEST_SCHEME_CODE = "TEST_T12_MASTER_001"


def build_record(
    scheme_name: str = "Task 12 Integration Fund",
    category: str = "Equity",
):
    return AMFISchemeDetailsProvider.normalize(
        scheme_code=TEST_SCHEME_CODE,
        scheme_name=scheme_name,
        isin="INTG00000001",
        amc_name="Task 12 Test AMC",
        category=category,
        sub_category="Large Cap",
        scheme_type="Open Ended",
        min_sip_amount="100",
        min_lumpsum="1000",
        returns_1y="10.50",
        returns_3y="12.25",
        returns_5y="14.10",
        expense_ratio="1.20",
        fund_manager="Task 12 Test Manager",
        fund_size_cr="5000",
        is_tax_saver=False,
        lock_in_years="0",
    )


def cleanup_test_scheme():
    with get_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM mf_schemes
                WHERE scheme_code = %s
                """,
                (TEST_SCHEME_CODE,),
            )

        connection.commit()


def test_master_sync_insert_and_update():
    cleanup_test_scheme()

    service = MutualFundMasterSyncService()

    try:
        # ---------------------------------------------------------
        # INSERT
        # ---------------------------------------------------------
        insert_result = service.sync(
            [build_record()]
        )

        assert insert_result == {
            "processed": 1,
            "inserted": 1,
            "updated": 0,
            "skipped": 0,
        }

        # Verify inserted record.
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        scheme_code,
                        scheme_name,
                        isin,
                        amc_name,
                        category,
                        sub_category,
                        scheme_type,
                        risk_level,
                        min_sip_amount,
                        min_lumpsum,
                        returns_1y,
                        returns_3y,
                        returns_5y,
                        expense_ratio,
                        fund_manager,
                        fund_size_cr,
                        is_tax_saver,
                        lock_in_years
                    FROM mf_schemes
                    WHERE scheme_code = %s
                    """,
                    (TEST_SCHEME_CODE,),
                )

                row = cursor.fetchone()

        assert row is not None

        assert row[0] == TEST_SCHEME_CODE
        assert row[1] == "Task 12 Integration Fund"
        assert row[2] == "INTG00000001"
        assert row[3] == "Task 12 Test AMC"
        assert row[4] == "Equity"
        assert row[5] == "Large Cap"
        assert row[6] == "Open Ended"

        # Riskometer is no longer populated.
        # The legacy database column is retained but nullable.
        assert row[7] is None

        assert row[8] == Decimal("100")
        assert row[9] == Decimal("1000")
        assert row[10] == Decimal("10.50")
        assert row[11] == Decimal("12.25")
        assert row[12] == Decimal("14.10")
        assert row[13] == Decimal("1.20")

        assert row[14] == "Task 12 Test Manager"
        assert row[15] == Decimal("5000")
        assert row[16] is False
        assert row[17] == Decimal("0")

        # ---------------------------------------------------------
        # UPDATE
        # ---------------------------------------------------------
        update_result = service.sync(
            [
                build_record(
                    scheme_name="Task 12 Updated Fund",
                    category="Hybrid",
                )
            ]
        )

        assert update_result == {
            "processed": 1,
            "inserted": 0,
            "updated": 1,
            "skipped": 0,
        }

        # Verify updated record.
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        scheme_name,
                        category,
                        amc_name,
                        scheme_type,
                        lock_in_years
                    FROM mf_schemes
                    WHERE scheme_code = %s
                    """,
                    (TEST_SCHEME_CODE,),
                )

                row = cursor.fetchone()

        assert row == (
            "Task 12 Updated Fund",
            "Hybrid",
            "Task 12 Test AMC",
            "Open Ended",
            Decimal("0"),
        )

    finally:
        # Always remove the temporary test record.
        cleanup_test_scheme()