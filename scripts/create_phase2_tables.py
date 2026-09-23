from pathlib import Path
from database.database import get_db_connection

ROOT = Path(__file__).resolve().parents[1]
SQL_FILE = ROOT / "database" / "phase2_schema.sql"


def main():
    sql = SQL_FILE.read_text(encoding="utf-8")
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        connection.commit()
        print("Phase 2 tables/schema are ready.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
