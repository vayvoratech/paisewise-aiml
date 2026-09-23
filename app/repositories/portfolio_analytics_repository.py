import json
from typing import Any

from app.db.session import get_db


class PortfolioAnalyticsRepository:
    """
    Handles PostgreSQL operations for portfolio analytics snapshots.
    """

    def save_snapshot(
        self,
        user_id: str,
        snapshot_date,
        analytics_data: dict[str, Any],
    ) -> None:
        query = """
            INSERT INTO portfolio_analytics (
                user_id,
                snapshot_date,
                analytics_data
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, snapshot_date)
            DO UPDATE SET
                analytics_data = EXCLUDED.analytics_data
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        user_id,
                        snapshot_date,
                        json.dumps(analytics_data),
                    ),
                )

    def get_history(
        self,
        user_id: str,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                id,
                user_id,
                snapshot_date,
                analytics_data,
                created_at
            FROM portfolio_analytics
            WHERE user_id = %s
            ORDER BY snapshot_date DESC
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (user_id,),
                )

                rows = cursor.fetchall()

                columns = [
                    desc.name
                    for desc in cursor.description
                ]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]