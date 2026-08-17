from sqlalchemy import text

from app.db.database import SessionLocal
from app.services.market_service import get_market


def fetch_market_data():
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT DISTINCT symbol
                FROM portfolio_holdings
                ORDER BY symbol
            """)
        ).mappings().all()

        market_data = []

        for row in rows:
            data = get_market(row["symbol"])
            if data:
                market_data.append(data)

        return market_data
    finally:
        db.close()
