from typing import Any

from app.db.session import get_db


class FraudOrderRepository:
    def get_order_by_id(
        self,
        order_id: str,
    ) -> dict[str, Any] | None:
        query = """
            SELECT
                id,
                user_id,
                symbol,
                side,
                shares,
                price_per_share,
                total_amount,
                order_type,
                xp_earned,
                created_at
            FROM practice.orders
            WHERE id = %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (order_id,))

                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))