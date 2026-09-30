from app.db.session import get_db


with get_db() as connection:
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            model,
            prompt_tokens,
            completion_tokens,
            cost,
            latency_ms,
            recorded_at
        FROM llm_usage
        ORDER BY recorded_at DESC
        LIMIT 5
        """
    )

    for row in cursor.fetchall():
        print(row)