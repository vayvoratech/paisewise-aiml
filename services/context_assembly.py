
from database.database import get_db_connection


def assemble_portfolio_context(user_id: str):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    SELECT symbol, quantity, avg_price
    FROM public.holdings
    WHERE user_id = %s
    """

    cursor.execute(query, (user_id,))

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    holdings = []

    for row in rows:
        holdings.append({
            "symbol": row[0],
            "quantity": float(row[1]),
            "current_price": float(row[2]) if row[2] is not None else None
        })

    return {
        "user_id": user_id,
        "holdings": holdings
    }

