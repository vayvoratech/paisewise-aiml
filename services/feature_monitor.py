
# Feature monitoring service
from database.database import get_db_connection


def get_daily_distribution():
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    SELECT
        quiz_attempts_total,
        quiz_pass_rate,
        avg_quiz_score
    FROM public.user_features
    WHERE computed_at::date = CURRENT_DATE
    """

    cursor.execute(query)
    records = cursor.fetchall()

    cursor.close()
    connection.close()

    if not records:
        return None

    count = len(records)

    totals = {
        "quiz_attempts_total": 0,
        "quiz_pass_rate": 0,
        "avg_quiz_score": 0
    }

    for record in records:
        totals["quiz_attempts_total"] += record[0] or 0
        totals["quiz_pass_rate"] += float(record[1] or 0)
        totals["avg_quiz_score"] += float(record[2] or 0)

    distribution = {}

    for key, value in totals.items():
        distribution[key] = round(value / count, 3)

    return distribution


def run_feature_monitoring():
    today_distribution = get_daily_distribution()

    if today_distribution is None:
        return {
            "message": "No feature data available for today"
        }

    return {
        "today_distribution": today_distribution
    }


if __name__ == "__main__":
    result = run_feature_monitoring()
    print(result)

