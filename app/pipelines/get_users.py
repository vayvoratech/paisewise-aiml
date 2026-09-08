from decimal import Decimal
from sqlalchemy import text
from app.db.database import SessionLocal


def _convert_decimal(value):
    return float(value) if isinstance(value, Decimal) else value


def get_users():

    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT DISTINCT
                u.user_id,
                u.full_name,
                'Hindi' AS preferred_language
            FROM public.users u
            INNER JOIN public.portfolio_holdings h
                ON h.user_id = u.user_id
            ORDER BY u.user_id
        """)).mappings().all()

        users = []

        for row in rows:
            user = {k: _convert_decimal(v) for k, v in row.items()}

            holdings = db.execute(text("""
                SELECT
                    symbol,
                    company_name,
                    quantity,
                    avg_buy_price,
                    NULL AS current_price
                FROM public.portfolio_holdings
                WHERE user_id = :user_id
                ORDER BY symbol
            """), {
                "user_id": row["user_id"]
            }).mappings().all()

            user["holdings"] = [
                {k: _convert_decimal(v) for k, v in holding.items()}
                for holding in holdings
            ]

            users.append(user)

        return users

    finally:
        db.close()
