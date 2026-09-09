from typing import Any

from app.db.session import get_db


class OrdersRepository:

    def get_orders(
        self,
        user_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
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
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id, limit))
                rows = cursor.fetchall()

                columns = [desc.name for desc in cursor.description]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]