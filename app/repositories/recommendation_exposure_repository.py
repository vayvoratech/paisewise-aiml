from __future__ import annotations

from datetime import datetime
from typing import Any

from app.db.session import get_db


class RecommendationExposureRepository:
    """Repository for persisted mutual-fund recommendation exposures."""

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

    @staticmethod
    def record_exposure(
        user_id: str,
        scheme_code: str,
        amc_name: str,
        recommendation_rank: int,
        recommendation_source: str,
        recommended_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Persist one fund recommendation exposure."""

        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        if not scheme_code or not scheme_code.strip():
            raise ValueError("scheme_code cannot be empty")

        if not amc_name or not amc_name.strip():
            raise ValueError("amc_name cannot be empty")

        if recommendation_rank <= 0:
            raise ValueError(
                "recommendation_rank must be greater than zero"
            )

        if (
            not recommendation_source
            or not recommendation_source.strip()
        ):
            raise ValueError(
                "recommendation_source cannot be empty"
            )

        query = """
            INSERT INTO recommendation_exposures (
                user_id,
                scheme_code,
                amc_name,
                recommendation_rank,
                recommendation_source,
                recommended_at
            )
            VALUES (%s, %s, %s, %s, %s, COALESCE(%s, NOW()))
            RETURNING
                id,
                user_id,
                scheme_code,
                amc_name,
                recommendation_rank,
                recommendation_source,
                recommended_at
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        user_id.strip(),
                        scheme_code.strip(),
                        amc_name.strip(),
                        recommendation_rank,
                        recommendation_source.strip(),
                        recommended_at,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise RuntimeError(
                        "Unable to record recommendation exposure."
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))

    def get_recent_user_exposures(
        self,
        user_id: str,
        *,
        days: int = 28,
    ) -> list[dict[str, Any]]:
        """Return a user's recommendation exposures for a time window."""

        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        if days <= 0:
            raise ValueError("days must be greater than zero")

        query = """
            SELECT
                id,
                user_id,
                scheme_code,
                amc_name,
                recommendation_rank,
                recommendation_source,
                recommended_at
            FROM recommendation_exposures
            WHERE user_id = %s
              AND recommended_at >= NOW() - (%s * INTERVAL '1 day')
            ORDER BY recommended_at DESC, recommendation_rank ASC
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        user_id.strip(),
                        days,
                    ),
                )

                rows = cursor.fetchall()

                return self._rows_to_dicts(cursor, rows)

    def get_user_scheme_exposure_count(
        self,
        user_id: str,
        scheme_code: str,
        *,
        days: int = 28,
    ) -> int:
        """Count recent exposures of one fund for one user."""

        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        if not scheme_code or not scheme_code.strip():
            raise ValueError("scheme_code cannot be empty")

        if days <= 0:
            raise ValueError("days must be greater than zero")

        query = """
            SELECT COUNT(*)
            FROM recommendation_exposures
            WHERE user_id = %s
              AND scheme_code = %s
              AND recommended_at >= NOW() - (%s * INTERVAL '1 day')
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        user_id.strip(),
                        scheme_code.strip(),
                        days,
                    ),
                )

                row = cursor.fetchone()

                return int(row[0]) if row else 0

    def get_monthly_amc_exposure(
        self,
        *,
        month_start: datetime,
        month_end: datetime,
    ) -> list[dict[str, Any]]:
        """Return AMC recommendation exposure counts for a period."""

        if month_end <= month_start:
            raise ValueError(
                "month_end must be greater than month_start"
            )

        query = """
            SELECT
                amc_name,
                COUNT(*) AS exposure_count,
                COUNT(DISTINCT user_id) AS unique_user_count,
                COUNT(DISTINCT scheme_code) AS unique_scheme_count
            FROM recommendation_exposures
            WHERE recommended_at >= %s
              AND recommended_at < %s
            GROUP BY amc_name
            ORDER BY exposure_count DESC, amc_name
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        month_start,
                        month_end,
                    ),
                )

                rows = cursor.fetchall()

                return self._rows_to_dicts(cursor, rows)