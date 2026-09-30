from __future__ import annotations

from collections.abc import Iterable

from app.db.session import get_db
from app.services.amfi_scheme_details_provider import (
    AMFISchemeDetailsRecord,
)


class MutualFundMasterSyncService:
    """
    Synchronizes normalized mutual-fund master records into
    the official mf_schemes table.

    Rules:
    - scheme_code is the stable identifier.
    - Required identity/schema fields must be present.
    - Existing non-null values are not replaced by NULL.
    - No synthetic/default business values are generated.
    - NAV synchronization remains the responsibility of
      MutualFundCatalogSyncService.
    """

    @staticmethod
    def _is_valid_record(
        record: AMFISchemeDetailsRecord,
    ) -> bool:
        return bool(
            str(record.scheme_code).strip()
            and str(record.scheme_name).strip()
            and str(record.amc_name).strip()
            and record.scheme_type
        )

    def sync(
        self,
        records: Iterable[AMFISchemeDetailsRecord],
    ) -> dict[str, int]:
        records = list(records)

        result = {
            "processed": 0,
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }

        if not records:
            return result

        with get_db() as connection:
            with connection.cursor() as cursor:
                for record in records:
                    result["processed"] += 1

                    if not self._is_valid_record(record):
                        result["skipped"] += 1
                        continue

                    cursor.execute(
                        """
                        SELECT scheme_code
                        FROM mf_schemes
                        WHERE scheme_code = %s
                        """,
                        (record.scheme_code,),
                    )

                    existing = cursor.fetchone()

                    if existing is None:
                        cursor.execute(
                            """
                            INSERT INTO mf_schemes (
                                scheme_code,
                                scheme_name,
                                isin,
                                amc_name,
                                category,
                                sub_category,
                                scheme_type,
                                min_sip_amount,
                                min_lumpsum,
                                returns_1y,
                                returns_3y,
                                returns_5y,
                                expense_ratio,
                                fund_manager,
                                fund_size_cr,
                                is_tax_saver,
                                lock_in_years,
                                is_active,
                                updated_at
                            )
                            VALUES (
                                %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, TRUE, NOW()
                            )
                            """,
                            (
                                record.scheme_code,
                                record.scheme_name,
                                record.isin,
                                record.amc_name,
                                record.category,
                                record.sub_category,
                                record.scheme_type,
                                record.min_sip_amount,
                                record.min_lumpsum,
                                record.returns_1y,
                                record.returns_3y,
                                record.returns_5y,
                                record.expense_ratio,
                                record.fund_manager,
                                record.fund_size_cr,
                                record.is_tax_saver,
                                record.lock_in_years,
                            ),
                        )

                        result["inserted"] += cursor.rowcount

                    else:
                        cursor.execute(
                            """
                            UPDATE mf_schemes
                            SET
                                scheme_name = %s,
                                isin = COALESCE(
                                    %s,
                                    isin
                                ),
                                amc_name = %s,
                                category = COALESCE(
                                    %s,
                                    category
                                ),
                                sub_category = COALESCE(
                                    %s,
                                    sub_category
                                ),
                                scheme_type = COALESCE(
                                    %s,
                                    scheme_type
                                ),
                                min_sip_amount = COALESCE(
                                    %s,
                                    min_sip_amount
                                ),
                                min_lumpsum = COALESCE(
                                    %s,
                                    min_lumpsum
                                ),
                                returns_1y = COALESCE(
                                    %s,
                                    returns_1y
                                ),
                                returns_3y = COALESCE(
                                    %s,
                                    returns_3y
                                ),
                                returns_5y = COALESCE(
                                    %s,
                                    returns_5y
                                ),
                                expense_ratio = COALESCE(
                                    %s,
                                    expense_ratio
                                ),
                                fund_manager = COALESCE(
                                    %s,
                                    fund_manager
                                ),
                                fund_size_cr = COALESCE(
                                    %s,
                                    fund_size_cr
                                ),
                                is_tax_saver = %s,
                                lock_in_years = COALESCE(
                                    %s,
                                    lock_in_years
                                ),
                                updated_at = NOW()
                            WHERE scheme_code = %s
                            """,
                            (
                                record.scheme_name,
                                record.isin,
                                record.amc_name,
                                record.category,
                                record.sub_category,
                                record.scheme_type,
                                record.min_sip_amount,
                                record.min_lumpsum,
                                record.returns_1y,
                                record.returns_3y,
                                record.returns_5y,
                                record.expense_ratio,
                                record.fund_manager,
                                record.fund_size_cr,
                                record.is_tax_saver,
                                record.lock_in_years,
                                record.scheme_code,
                            ),
                        )

                        result["updated"] += cursor.rowcount

            connection.commit()

        return result