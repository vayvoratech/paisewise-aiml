from database.database import get_db_connection
from datetime import date
import json


def get_daily_distribution():

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    SELECT feature_vector
    FROM feature_vectors
    WHERE created_at::date = CURRENT_DATE
    """

    cursor.execute(query)

    records = cursor.fetchall()

    cursor.close()
    connection.close()


    if not records:
        return None


    totals = {}
    count = len(records)


    for record in records:

        features = record[0]

        for key, value in features.items():

            if key not in totals:
                totals[key] = 0

            totals[key] += value


    distribution = {}

    for key, value in totals.items():
        distribution[key] = value / count


    return distribution



def save_distribution(distribution):

    connection = get_db_connection()
    cursor = connection.cursor()


    for feature_name, average_value in distribution.items():

        check_query = """
        SELECT id
        FROM feature_distribution_history
        WHERE date = %s
        AND feature_name = %s
        """

        cursor.execute(
            check_query,
            (
                date.today(),
                feature_name
            )
        )


        existing_record = cursor.fetchone()


        if existing_record:
            continue


        insert_query = """
        INSERT INTO feature_distribution_history
        (date, feature_name, average_value)
        VALUES (%s, %s, %s)
        """


        cursor.execute(
            insert_query,
            (
                date.today(),
                feature_name,
                average_value
            )
        )


    connection.commit()

    cursor.close()
    connection.close()



def get_previous_distribution():

    connection = get_db_connection()
    cursor = connection.cursor()


    query = """
    SELECT feature_name, average_value
    FROM feature_distribution_history
    WHERE date = CURRENT_DATE - INTERVAL '1 day'
    """


    cursor.execute(query)

    records = cursor.fetchall()


    cursor.close()
    connection.close()


    if not records:
        return None


    distribution = {}


    for record in records:

        feature_name = record[0]
        average_value = record[1]

        distribution[feature_name] = average_value


    return distribution



def calculate_shift(old_distribution, new_distribution):

    alerts = []

    threshold = 20


    for feature in old_distribution:

        if feature in new_distribution:

            old_value = old_distribution[feature]
            new_value = new_distribution[feature]


            if old_value == 0:
                continue


            change_percentage = (
                abs(new_value - old_value)
                / old_value
            ) * 100


            if change_percentage > threshold:

                alerts.append({
                    "feature": feature,
                    "change_percentage": round(change_percentage, 2),
                    "message": "Feature distribution shifted more than 20%"
                })


    return alerts



def run_feature_monitoring():

    today_distribution = get_daily_distribution()


    if today_distribution is None:

        return {
            "message": "No feature data available for today"
        }


    save_distribution(today_distribution)


    previous_distribution = get_previous_distribution()


    if previous_distribution is None:

        return {
            "message": "No previous distribution available",
            "today_distribution": today_distribution
        }


    alerts = calculate_shift(
        previous_distribution,
        today_distribution
    )


    return {
        "today_distribution": today_distribution,
        "alerts": alerts
    }



if __name__ == "__main__":

    result = run_feature_monitoring()

    print(result)