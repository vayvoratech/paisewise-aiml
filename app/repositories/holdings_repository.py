from typing import Any

from app.db.session import get_db


class HoldingsRepository:
    def get_holdings(
        self,
        user_id: str,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                id,
                user_id,
                symbol,
                name,
                emoji,
                shares,
                avg_price,
                current_price,
                note
            FROM portfolio.holdings
            WHERE user_id = %s
            ORDER BY symbol
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

    def get_users_with_more_than_two_holdings(
        self,
    ) -> list[str]:
        query = """
            SELECT user_id
            FROM portfolio.holdings
            GROUP BY user_id
            HAVING COUNT(*) > 2
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)

                rows = cursor.fetchall()

                return [
                    str(row[0])
                    for row in rows
                ]