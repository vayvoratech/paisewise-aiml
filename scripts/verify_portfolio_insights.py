from sqlalchemy import text

from app.db.database import SessionLocal


def verify_saved_insights():
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT COUNT(*) AS insight_count
                FROM portfolio_insights
            """)
        ).mappings().one()

        print(f"Portfolio insights stored: {result['insight_count']}")
        return result["insight_count"]
    finally:
        db.close()


if __name__ == "__main__":
    verify_saved_insights()
