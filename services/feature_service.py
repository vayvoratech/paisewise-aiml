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
from datetime import datetime
import json


def refresh_features(user_id):

    # -----------------------------
    # Placeholder feature calculation
    # Replace with actual calculation later
    # -----------------------------
    feature_vector = {
        "risk_score": 0.72,
        "portfolio_value": 125000,
        "diversification_score": 0.84
    }

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO feature_vectors
    (user_id, feature_vector, created_at)
    VALUES (%s, %s, %s)
    """

    cursor.execute(
        query,
        (
            user_id,
            json.dumps(feature_vector),
            datetime.utcnow()
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "status": "success",
        "message": "Features refreshed successfully",
        "user_id": user_id,
        "features": feature_vector
    }