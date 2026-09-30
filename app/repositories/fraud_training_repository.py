from typing import Any

from app.db.session import get_db


class FraudTrainingRepository:
    """Retrieves compliance-reviewed fraud cases for model training."""

    def get_reviewed_cases(self) -> list[dict[str, Any]]:
        query = """
            SELECT
                fc.id AS fraud_case_id,
                fc.order_id,
                fc.reviewer_decision,
                o.user_id,
                o.symbol,
                o.side,
                o.shares,
                o.price_per_share,
                o.total_amount,
                o.order_type,
                o.xp_earned,
                o.created_at
            FROM fraud_cases AS fc
            INNER JOIN practice.orders AS o
                ON o.id = fc.order_id
            WHERE fc.reviewer_decision IN (
                'TRUE_FRAUD',
                'FALSE_POSITIVE'
            )
            ORDER BY fc.reviewed_at ASC
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