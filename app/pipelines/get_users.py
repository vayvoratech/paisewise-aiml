from decimal import Decimal

from sqlalchemy import text

from app.db.database import SessionLocal


def _convert_decimal(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def get_users():
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT DISTINCT
                    u.user_id,
                    u.full_name,
                    u.age,
                    
                    u.risk_profile,
                    u.monthly_investment,
                    COALESCE(uf.preferred_language, 'hi') AS preferred_language

                FROM users u
                INNER JOIN portfolio_holdings p
                    ON u.user_id = p.user_id
                LEFT JOIN user_features uf
                    ON u.user_id = uf.user_id
                ORDER BY u.user_id
            """)

        ).mappings().all()

        users = []

        for row in rows:
            user = {
                key: _convert_decimal(value)
                for key, value in row.items()
            }

            holdings = db.execute(
                text("""
                    SELECT
                        symbol,
                        company_name,
                        quantity,
                        avg_buy_price
                    FROM portfolio_holdings
                    WHERE user_id = :user_id
                    ORDER BY symbol
                """),
                
                {"user_id": row["user_id"]},
            ).mappings().all()

            user["holdings"] = [
                {
                    key: _convert_decimal(value)
                    for key, value in holding.items()
                }
                for holding in holdings
            ]

            users.append(user)

        return users

    finally:
        db.close()
