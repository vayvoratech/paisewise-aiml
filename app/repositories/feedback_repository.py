from typing import Any

from app.db.session import get_db


class FeedbackRepository:
    """
    Repository for AI chat feedback.
    """

    def create_feedback(
        self,
        response_id: str,
        user_id: str,
        category: str,
        feedback: str,
    ) -> dict[str, Any]:

        query = """
            INSERT INTO public.chat_feedback (
                response_id,
                user_id,
                category,
                feedback
            )
            VALUES (%s, %s, %s, %s)
            RETURNING
                id,
                response_id,
                user_id,
                category,
                feedback,
                created_at
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        response_id,
                        user_id,
                        category,
                        feedback,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise RuntimeError(
                        "Failed to create chat feedback"
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(
                    zip(columns, row)
                )

    def get_weekly_analytics(
        self,
    ) -> list[dict[str, Any]]:

        query = """
            SELECT
                category,
                COUNT(*) FILTER (
                    WHERE feedback = 'up'
                ) AS thumbs_up,
                COUNT(*) FILTER (
                    WHERE feedback = 'down'
                ) AS thumbs_down,
                COUNT(*) AS total_feedback
            FROM public.chat_feedback
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY category
            ORDER BY category
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)

                rows = cursor.fetchall()

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]