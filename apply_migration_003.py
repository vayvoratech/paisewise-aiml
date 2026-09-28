from pathlib import Path

from app.db.session import get_db


migration_file = Path("migrations/003_llm_usage_performance.sql")
sql = migration_file.read_text(encoding="utf-8")


with get_db() as connection:
    cursor = connection.cursor()
    cursor.execute(sql)

print("Migration 003 applied successfully.")