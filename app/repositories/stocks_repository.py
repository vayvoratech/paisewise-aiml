from typing import Any

from app.db.session import get_db


class StocksRepository:
    """
    Repository for reading available stock data.

    This repository only accesses stock-market data.
    It does not access user-specific portfolio data.
    """

    def get_stocks(self) -> list[dict[str, Any]]:
        query = """
            SELECT
                symbol,
                name,
                price,
                change_pct,
                emoji,
                trend_json
            FROM practice.stocks
            ORDER BY symbol
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)

                rows = cursor.fetchall()

                columns = [
                    desc.name
                    for desc in cursor.description
                ]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]

    def get_stock(
        self,
        symbol: str,
    ) -> dict[str, Any] | None:

        if not symbol or not symbol.strip():
            raise ValueError(
                "symbol cannot be empty"
            )

        query = """
            SELECT
                symbol,
                name,
                price,
                change_pct,
                emoji,
                trend_json
            FROM practice.stocks
            WHERE UPPER(symbol) = UPPER(%s)
            LIMIT 1
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (symbol.strip(),),
                )

                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [
                    desc.name
                    for desc in cursor.description
                ]

                return dict(
                    zip(columns, row)
                )