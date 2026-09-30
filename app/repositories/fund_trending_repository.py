from __future__ import annotations

from typing import Any

from app.db.session import get_db


class FundTrendingRepository:
    """Repository for learner-level mutual-fund popularity."""

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

    def get_trending_for_level(
        self,
        level: int,
        *,
        days: int = 28,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Return funds most frequently recommended to users
        at a learner level.

        Only persisted recommendation exposures are used.
        If there is no real exposure data, an empty list is returned.
        """

        if level < 1:
            raise ValueError(
                "level must be greater than zero"
            )

        if days <= 0:
            raise ValueError(
                "days must be greater than zero"
            )

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

        query = """
            SELECT
                re.scheme_code,
                fs.scheme_name,
                re.amc_name,
                COUNT(*) AS exposure_count,
                COUNT(DISTINCT re.user_id) AS unique_user_count
            FROM recommendation_exposures AS re
            INNER JOIN mf_schemes AS fs
                ON fs.scheme_code = re.scheme_code
            INNER JOIN profile.profiles AS p
                ON p.user_id::text = re.user_id::text
            WHERE p.level = %s
              AND re.recommended_at >= NOW()
                  - (%s * INTERVAL '1 day')
            GROUP BY
                re.scheme_code,
                fs.scheme_name,
                re.amc_name
            ORDER BY
                exposure_count DESC,
                unique_user_count DESC,
                re.scheme_code
            LIMIT %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        level,
                        days,
                        limit,
                    ),
                )

                rows = cursor.fetchall()

                return self._rows_to_dicts(
                    cursor,
                    rows,
                )