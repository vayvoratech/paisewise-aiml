from app.db.session import get_db


with get_db() as connection:
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'llm_usage'
        ORDER BY ordinal_position
        """
    )

    for row in cursor.fetchall():
        print(row)