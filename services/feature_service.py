from database.database import get_db_connection


def get_latest_features(user_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
    SELECT user_id, feature_vector, created_at
    FROM feature_vectors
    WHERE user_id = %s
    ORDER BY created_at DESC
    LIMIT 1
    """

    cursor.execute(query, (user_id,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result is None:
        return None

    return {
        "user_id": result[0],
        "features": result[1],
        "updated_at": str(result[2])
    }