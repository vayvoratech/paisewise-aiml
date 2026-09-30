from pathlib import Path

from app.db.session import get_db


migration_path = Path("migrations/ai_request_replay.sql")

if not migration_path.exists():
    raise FileNotFoundError(
        f"Migration file not found: {migration_path}"
    )

sql = migration_path.read_text(encoding="utf-8")

with get_db() as connection:
    with connection.cursor() as cursor:
        cursor.execute(sql)

print("AI request replay migration applied successfully.")