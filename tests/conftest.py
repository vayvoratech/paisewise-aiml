import os

from dotenv import load_dotenv
import pytest

load_dotenv()
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("GEMINI_MODEL", "test-model")


@pytest.fixture(scope="session", autouse=True)
def initialize_audit_log_for_integration_tests():
    """Prepare the audit fixture when PostgreSQL is available."""
    try:
        from database.database import get_db_connection
    except ModuleNotFoundError:
        return

    try:
        connection = get_db_connection()
    except Exception:
        return

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO audit_log (user_id, action, entity_type, device_id, result)
                    SELECT %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM audit_log WHERE user_id = %s AND device_id = %s
                    )
                    """,
                    (
                        "22222222-2222-2222-2222-222222222222",
                        "DEVICE_FIRST_SEEN",
                        "USER",
                        "device-001",
                        "SUCCESS",
                        "22222222-2222-2222-2222-222222222222",
                        "device-001",
                    ),
                )
            connection.commit()
    except Exception:
        return
