from datetime import datetime

from app.db.session import get_db


class FraudWeeklySummaryRepository:
    """Reads fraud cases required for the weekly fraud summary."""

    def get_cases_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict]:
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        order_id,
                        fraud_score,
                        status,
                        reviewer_decision,
                        reviewed_at,
                        created_at,
                        updated_at
                    FROM fraud_cases
                    WHERE created_at >= %s
                      AND created_at <= %s
                    ORDER BY created_at ASC
                    """,
                    (start_date, end_date),
                )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]