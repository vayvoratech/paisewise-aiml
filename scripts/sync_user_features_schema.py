
from sqlalchemy import inspect, text

from app.db.database import engine


MISSING_COLUMNS = {
    "total_xp": "INTEGER DEFAULT 0",
    "preferred_language": "VARCHAR(30)",
    "onboarding_goal": "VARCHAR(100)",
    "age_proxy": "SMALLINT",
    "city_tier": "VARCHAR(20)",
    "time_of_day": "VARCHAR(20)",
    "session_duration": "INTEGER DEFAULT 0",
    "screens_visited": "INTEGER DEFAULT 0",
    "lessons_started": "INTEGER DEFAULT 0",
    "quizzes_taken": "INTEGER DEFAULT 0",
}


def sync_user_features_schema():
    inspector = inspect(engine)
    existing = {
        column["name"]
        for column in inspector.get_columns("user_features")
    }

    missing = [
        (name, definition)
        for name, definition in MISSING_COLUMNS.items()
        if name not in existing
    ]

    if not missing:
        print("user_features schema is already up to date.")
        return

    with engine.begin() as connection:
        for name, definition in missing:
            connection.execute(
                text(
                    f'ALTER TABLE user_features '
                    f'ADD COLUMN IF NOT EXISTS "{name}" {definition}'
                )
            )
            print(f"Added user_features.{name}")

    print(f"Schema sync completed. Added {len(missing)} column(s).")


if __name__ == "__main__":
    sync_user_features_schema()
