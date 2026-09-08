from datetime import datetime
from typing import Any

from app.db.session import get_db


class UserFeaturesRepository:
    """
    Repository for ML features and stored churn scores.

    Database access stays inside this repository.
    """

    def get_features(self, user_id: str) -> dict[str, Any] | None:
        query = """
            SELECT
                user_id,
                days_since_last_active,
                sessions_7d,
                lessons_completed_7d,
                chapters_completed,
                days_since_registration,
                notification_open_rate_30d,
                paper_trades_total,
                paper_trades_7d,
                has_real_investment
            FROM public.user_features
            WHERE user_id = %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [desc.name for desc in cursor.description]
                return dict(zip(columns, row))

    def update_churn_score(
        self,
        user_id: str,
        churn_score: float,
        computed_at: datetime,
    ) -> None:
        update_features_query = """
            UPDATE public.user_features
            SET
                churn_score = %s,
                churn_score_computed_at = %s,
                updated_at = NOW()
            WHERE user_id = %s
        """

        insert_history_query = """
            INSERT INTO public.user_churn_scores (
                user_id,
                score,
                computed_at
            )
            VALUES (%s, %s, %s)
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    update_features_query,
                    (churn_score, computed_at, user_id),
                )

                cursor.execute(
                    insert_history_query,
                    (user_id, churn_score, computed_at),
                )