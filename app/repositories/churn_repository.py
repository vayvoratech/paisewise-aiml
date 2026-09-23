from datetime import datetime, timezone
from typing import Any

from app.db.session import get_db


class ChurnRepository:
    def save_score(
        self,
        user_id: str,
        score: float,
        computed_at: datetime | None = None,
    ) -> None:
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        if computed_at is None:
            computed_at = datetime.now(timezone.utc)

        query = """
            INSERT INTO user_churn_scores (
                user_id,
                score,
                computed_at
            )
            VALUES (%s, %s, %s)
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        user_id.strip(),
                        score,
                        computed_at,
                    ),
                )

    def get_latest_score(
        self,
        user_id: str,
    ) -> dict[str, Any] | None:
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        query = """
            SELECT
                user_id,
                score,
                computed_at
            FROM user_churn_scores
            WHERE user_id = %s
            ORDER BY computed_at DESC
            LIMIT 1
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id.strip(),))
                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [desc.name for desc in cursor.description]

                return dict(zip(columns, row))