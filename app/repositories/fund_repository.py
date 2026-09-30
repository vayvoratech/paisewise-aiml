from __future__ import annotations

from typing import Any

from app.db.session import get_db


class FundRepository:
    """Repository for the official mutual-fund scheme catalog."""

    _BASE_COLUMNS = """
        scheme_code,
        isin,
        scheme_name,
        amc_name,
        amc_code,
        category,
        sub_category,
        scheme_type,
        nav,
        nav_date,
        min_sip_amount,
        min_lumpsum,
        sip_multiplier,
        returns_1y,
        returns_3y,
        returns_5y,
        returns_since_launch,
        benchmark_name,
        benchmark_returns_1y,
        expense_ratio,
        fund_manager,
        fund_size_cr,
        launch_date,
        is_active,
        is_tax_saver,
        lock_in_years,
        dividend_option,
        growth_option,
        bse_scheme_code,
        nse_symbol,
        updated_at
    """

    @staticmethod
    def _rows_to_dicts(
        cursor: Any,
        rows: list[Any],
    ) -> list[dict[str, Any]]:
        columns = [
            description.name
            for description in cursor.description
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    def get_active_funds(self) -> list[dict[str, Any]]:
        """Return all active mutual-fund schemes."""
        query = f"""
            SELECT
                {self._BASE_COLUMNS}
            FROM mf_schemes
            WHERE is_active = TRUE
            ORDER BY scheme_name
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

                return self._rows_to_dicts(cursor, rows)

    def get_active_funds_by_category(
        self,
        category: str,
    ) -> list[dict[str, Any]]:
        """Return active mutual-fund schemes for a category."""
        if not category or not category.strip():
            raise ValueError("category cannot be empty")

        query = f"""
            SELECT
                {self._BASE_COLUMNS}
            FROM mf_schemes
            WHERE is_active = TRUE
              AND category = %s
            ORDER BY scheme_name
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (category.strip(),))
                rows = cursor.fetchall()

                return self._rows_to_dicts(cursor, rows)

    def get_active_funds_by_amc(
        self,
        amc_name: str,
    ) -> list[dict[str, Any]]:
        """Return active mutual-fund schemes managed by an AMC."""
        if not amc_name or not amc_name.strip():
            raise ValueError("amc_name cannot be empty")

        query = f"""
            SELECT
                {self._BASE_COLUMNS}
            FROM mf_schemes
            WHERE is_active = TRUE
              AND amc_name = %s
            ORDER BY scheme_name
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (amc_name.strip(),))
                rows = cursor.fetchall()

                return self._rows_to_dicts(cursor, rows)

    def get_by_scheme_code(
        self,
        scheme_code: str,
    ) -> dict[str, Any] | None:
        """Return a mutual-fund scheme by its official scheme code."""
        if not scheme_code or not scheme_code.strip():
            raise ValueError("scheme_code cannot be empty")

        query = f"""
            SELECT
                {self._BASE_COLUMNS}
            FROM mf_schemes
            WHERE scheme_code = %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (scheme_code.strip(),))
                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))