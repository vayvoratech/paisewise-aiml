from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from app.db.session import get_db


class UserRepository:
    def get_users_registered_on(
        self, target_date: date
    ) -> list[dict[str, Any]]:
        start = datetime.combine(
            target_date,
            time.min,
            tzinfo=timezone.utc,
        )
        end = start + timedelta(days=1)

        query = """
            SELECT
                id,
                name,
                created_at
            FROM auth.users
            WHERE created_at >= %s
              AND created_at < %s
            ORDER BY created_at
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (start, end))
                rows = cursor.fetchall()
                columns = [desc.name for desc in cursor.description]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]