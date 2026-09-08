from sqlalchemy import text

from app.db.database import SessionLocal


LOOKBACK_DAYS = 90


def extract_user_behaviour():
    db = SessionLocal()

    try:
        tables = {
            "lesson_progress": "completed_at",
            "quiz_attempts": "attempted_at",
            "paper_trades": "created_at",
            "user_sessions": "login_time",
        }
        result = {}

        for table, date_column in tables.items():
            rows = db.execute(
                text(f"""
                    SELECT *
                    FROM {table}
                    WHERE {date_column} >= CURRENT_TIMESTAMP - INTERVAL '90 days'
                    ORDER BY {date_column}
                """)
            ).mappings().all()
            result[table] = rows

        return result
    finally:
        db.close()


if __name__ == "__main__":
    data = extract_user_behaviour()
    for name, rows in data.items():
        print(f"{name}: {len(rows)} rows")
