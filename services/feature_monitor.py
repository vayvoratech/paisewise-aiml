
# Feature monitoring service
from database.database import get_db_connection


def get_daily_distribution():
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    SELECT
        quizzes_taken,
        quiz_avg_score
    FROM public.user_features
    WHERE updated_at::date = CURRENT_DATE
    """

    cursor.execute(query)
    records = cursor.fetchall()

    cursor.close()
    connection.close()

    if not records:
        return None

    count = len(records)

    totals = {
        "quizzes_taken": 0,
        "quiz_avg_score": 0
    }

    for record in records:
        totals["quizzes_taken"] += record[0] or 0
        totals["quiz_avg_score"] += float(record[1] or 0)

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

def calculate_shift(old_distribution, new_distribution):

    alerts = []

    for feature, old_value in old_distribution.items():

        if feature in new_distribution:

            new_value = new_distribution[feature]

            if old_value == 0:
                continue

            change = abs(
                new_value - old_value
            ) / old_value


            if change > 0.20:

                alerts.append(
                    {
                        "feature": feature,
                        "old_value": old_value,
                        "new_value": new_value,
                        "change_percentage": round(change * 100, 2)
                    }
                )

    return alerts