from typing import Any

from app.db.session import get_db


class ProfileRepository:

    def get_profile(self, user_id: str) -> dict[str, Any] | None:
        query = """
            SELECT
                user_id,
                name,
                handle,
                city,
                level,
                day_streak,
                xp_total,
                lessons_completed,
                language,
                daily_reminders,
                kyc_verified
            FROM profile.profiles
            WHERE user_id = %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [desc.name for desc in cursor.description]
                return dict(zip(columns, row))