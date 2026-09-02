
import os
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("GEMINI_MODEL", "test-model")


import pytest


@pytest.fixture(scope="session", autouse=True)
def initialize_audit_log_for_integration_tests():
    """Ensure audit-log integration tests have the required table and known device fixture."""
    try:
        from database.database import get_db_connection

        connection = get_db_connection()
        try:
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
        finally:
            connection.close()
    except Exception as exc:
        pytest.fail(f"Audit-log test database initialization failed: {exc}")
