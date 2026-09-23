from datetime import datetime
from typing import Any

from app.db.session import get_db


class ChurnReengagementRepository:
    """
    Stores re-engagement campaign assignments and tracks
    whether the user re-engaged within 7 days.
    """

    def create_campaign(
        self,
        user_id: str,
        churn_score: float,
        variant: str,
        message: str,
        sent_at: datetime | None = None,
    ) -> dict[str, Any]:
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        if variant not in {"ai", "template"}:
            raise ValueError("variant must be 'ai' or 'template'")

        if not message or not message.strip():
            raise ValueError("message cannot be empty")

        query = """
            INSERT INTO public.churn_reengagement_tracking (
                user_id,
                churn_score,
                variant,
                message,
                sent_at
            )
            VALUES (%s, %s, %s, %s, COALESCE(%s, NOW()))
            RETURNING
                id,
                user_id,
                churn_score,
                variant,
                message,
                sent_at,
                reengaged_at,
                reengaged_within_7d,
                created_at
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        user_id.strip(),
                        float(churn_score),
                        variant,
                        message.strip(),
                        sent_at,
                    ),
                )
                row = cursor.fetchone()
                columns = [
                    description.name
                    for description in cursor.description
                ]

        return dict(zip(columns, row))

    def mark_reengaged(self, user_id: str) -> int:
        """
        Mark open campaign records as re-engaged when the user
        returns within 7 days of the notification.
        """

        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        query = """
            UPDATE public.churn_reengagement_tracking
            SET
                reengaged_at = COALESCE(reengaged_at, NOW()),
                reengaged_within_7d = TRUE
            WHERE user_id = %s
              AND reengaged_within_7d = FALSE
              AND sent_at <= NOW()
              AND sent_at >= NOW() - INTERVAL '7 days'
            RETURNING id
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id.strip(),))
                rows = cursor.fetchall()

        return len(rows)

    def get_weekly_summary(self) -> list[dict[str, Any]]:
        """
        Return weekly A/B-test performance for the last 7 days.
        """

        query = """
            SELECT
                variant,
                COUNT(*) AS notifications_sent,
                COUNT(*) FILTER (
                    WHERE reengaged_within_7d = TRUE
                ) AS reengaged_users,
                ROUND(
                    COUNT(*) FILTER (
                        WHERE reengaged_within_7d = TRUE
                    )::numeric
                    / NULLIF(COUNT(*), 0),
                    4
                ) AS reengagement_rate
            FROM public.churn_reengagement_tracking
            WHERE sent_at >= NOW() - INTERVAL '7 days'
            GROUP BY variant
            ORDER BY variant
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [
                    description.name
                    for description in cursor.description
                ]

        return [dict(zip(columns, row)) for row in rows]

    def get_weekly_churn_distribution(self) -> dict[str, Any]:
        """
        Return the weekly distribution of churn-risk levels
        for the product team dashboard.

        Uses the latest churn score for each user from the
        last 7 days.
        """

        query = """
            WITH latest_scores AS (
                SELECT DISTINCT ON (user_id)
                    user_id,
                    score,
                    computed_at
                FROM public.user_churn_scores
                WHERE computed_at >= NOW() - INTERVAL '7 days'
                ORDER BY user_id, computed_at DESC
            ),
            risk_distribution AS (
                SELECT
                    CASE
                        WHEN score > 0.7 THEN 'high'
                        WHEN score >= 0.4 THEN 'medium'
                        ELSE 'low'
                    END AS risk_level,
                    COUNT(*) AS user_count
                FROM latest_scores
                GROUP BY
                    CASE
                        WHEN score > 0.7 THEN 'high'
                        WHEN score >= 0.4 THEN 'medium'
                        ELSE 'low'
                    END
            ),
            totals AS (
                SELECT COUNT(*) AS total_users
                FROM latest_scores
            )
            SELECT
                totals.total_users,
                COALESCE(
                    (
                        SELECT user_count
                        FROM risk_distribution
                        WHERE risk_level = 'low'
                    ),
                    0
                ) AS low_count,
                COALESCE(
                    (
                        SELECT user_count
                        FROM risk_distribution
                        WHERE risk_level = 'medium'
                    ),
                    0
                ) AS medium_count,
                COALESCE(
                    (
                        SELECT user_count
                        FROM risk_distribution
                        WHERE risk_level = 'high'
                    ),
                    0
                ) AS high_count
            FROM totals
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()

        if row is None:
            return {
                "total_users": 0,
                "low": {
                    "count": 0,
                    "percentage": 0.0,
                },
                "medium": {
                    "count": 0,
                    "percentage": 0.0,
                },
                "high": {
                    "count": 0,
                    "percentage": 0.0,
                },
            }

        total_users, low_count, medium_count, high_count = row

        total_users = int(total_users or 0)
        low_count = int(low_count or 0)
        medium_count = int(medium_count or 0)
        high_count = int(high_count or 0)

        def percentage(count: int) -> float:
            if total_users == 0:
                return 0.0

            return round(
                (count / total_users) * 100,
                2,
            )

        return {
            "total_users": total_users,
            "low": {
                "count": low_count,
                "percentage": percentage(low_count),
            },
            "medium": {
                "count": medium_count,
                "percentage": percentage(medium_count),
            },
            "high": {
                "count": high_count,
                "percentage": percentage(high_count),
            },
        }