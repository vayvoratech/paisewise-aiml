from app.db.session import get_db


with get_db() as connection:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'ai_request_replays'
        """)

        count = cursor.fetchone()[0]

print(f"ai_request_replays table count: {count}")