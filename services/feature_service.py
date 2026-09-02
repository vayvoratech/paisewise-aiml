from database.database import get_db_connection


def get_latest_features(user_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT user_id, quizzes_taken, NULL, quiz_avg_score, updated_at
            FROM user_features
            WHERE user_id = %s
            LIMIT 1
            """,
            (user_id,),
        )
        result = cursor.fetchone()
        cursor.close()
    finally:
        connection.close()

    if result is None:
        return None

    return {
        "user_id": str(result[0]),
        "features": {
            "quiz_attempts_total": result[1],
            "quiz_pass_rate": float(result[2]) if result[2] is not None else None,
            "avg_quiz_score": float(result[3]) if result[3] is not None else None,
        },
        "updated_at": result[4].isoformat() if result[4] is not None else None,
    }
