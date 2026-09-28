from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.db.session import get_db
from app.services.amfi_nav_provider import AMFINAVRecord


class MutualFundCatalogSyncService:
    """
    Synchronizes AMFI NAV/identity data into existing mf_schemes records.

    This service deliberately does not create incomplete fund records.
    Only schemes already present in the official mf_schemes catalog are
    eligible for NAV synchronization.
    """

    def sync(self, records: Iterable[AMFINAVRecord]) -> dict[str, int]:
        records = list(records)

        if not records:
            return {
                "processed": 0,
                "updated": 0,
                "skipped": 0,
            }

        processed = 0
        updated = 0
        skipped = 0

        with get_db() as connection:
            with connection.cursor() as cursor:
                for record in records:
                    processed += 1

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
                        skipped += 1
                        continue

                    cursor.execute(
                        """
                        UPDATE mf_schemes
                        SET
                            isin = COALESCE(%s, isin),
                            nav = %s,
                            nav_date = %s,
                            updated_at = NOW()
                        WHERE scheme_code = %s
                        """,
                        (
                            record.isin_growth,
                            record.nav,
                            record.nav_date,
                            record.scheme_code,
                        ),
                    )

                    updated += cursor.rowcount

            connection.commit()

        return {
            "processed": processed,
            "updated": updated,
            "skipped": skipped,
        }