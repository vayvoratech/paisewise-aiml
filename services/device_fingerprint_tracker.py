from uuid import UUID

from database.database import get_db_connection


def is_new_device(user_id: UUID, device_id: str) -> bool:
    """
    Check whether this device has previously been seen for this user.

    Returns:
        True  -> device has not been seen for this user before
        False -> device is already known for this user
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM audit_log
                WHERE user_id = %s
                  AND device_id = %s
                LIMIT 1
                """,
                (str(user_id), device_id),
            )

            return cursor.fetchone() is None

    finally:
        connection.close()


def track_device(user_id: UUID, device_id: str) -> bool:
    """
    Track a device for a user.

    Returns:
        True  -> this was a new device for the user
        False -> this device was already known
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM audit_log
                WHERE user_id = %s
                  AND device_id = %s
                LIMIT 1
                """,
                (str(user_id), device_id),
            )

            is_new = cursor.fetchone() is None

            if is_new:
                cursor.execute(
                    """
                    INSERT INTO audit_log (
                        user_id,
                        action,
                        entity_type,
                        device_id,
                        result
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        str(user_id),
                        "DEVICE_FIRST_SEEN",
                        "USER",
                        device_id,
                        "SUCCESS",
                    ),
                )

                connection.commit()

            return is_new

    finally:
        connection.close()