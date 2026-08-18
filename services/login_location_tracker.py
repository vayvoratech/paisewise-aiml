from uuid import UUID

from database.database import get_db_connection


def track_login_location(
    user_id: UUID,
    ip_address: str,
    city: str,
) -> dict:
    """
    Record the approximate city of a login.

    Returns:
        Dictionary containing the current city and whether
        it differs from the user's previous login city.
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT new_values->>'city'
                FROM audit_log
                WHERE user_id = %s
                  AND action = 'LOGIN_LOCATION_RECORDED'
                  AND new_values->>'city' IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (str(user_id),),
            )

            row = cursor.fetchone()

            previous_city = row[0] if row else None
            location_changed = (
                previous_city is not None
                and previous_city.lower() != city.lower()
            )

            cursor.execute(
                """
                INSERT INTO audit_log (
                    user_id,
                    action,
                    entity_type,
                    new_values,
                    ip_address,
                    result
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s::jsonb,
                    %s,
                    %s
                )
                """,
                (
                    str(user_id),
                    "LOGIN_LOCATION_RECORDED",
                    "USER",
                    (
                        '{"city": "' + city.replace('"', '\\"') +
                        '", "location_changed": ' +
                        str(location_changed).lower() +
                        (
                            ', "previous_city": "' +
                            previous_city.replace('"', '\\"') + '"'
                            if previous_city
                            else ""
                        ) +
                        "}"
                    ),
                    ip_address,
                    "SUCCESS",
                ),
            )

            connection.commit()

            return {
                "city": city,
                "previous_city": previous_city,
                "location_changed": location_changed,
            }

    finally:
        connection.close()