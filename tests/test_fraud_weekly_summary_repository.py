from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.repositories.fraud_weekly_summary_repository import (
    FraudWeeklySummaryRepository,
)


START_DATE = datetime(
    2026,
    9,
    15,
    tzinfo=timezone.utc,
)

END_DATE = datetime(
    2026,
    9,
    22,
    tzinfo=timezone.utc,
)


def test_get_cases_between_returns_fraud_cases():
    repository = FraudWeeklySummaryRepository()

    cursor = MagicMock()

    # Explicitly set the column names returned by PostgreSQL.
    cursor.description = [
        type("Column", (), {"name": "id"})(),
        type("Column", (), {"name": "order_id"})(),
        type("Column", (), {"name": "fraud_score"})(),
        type("Column", (), {"name": "status"})(),
        type("Column", (), {"name": "reviewer_decision"})(),
        type("Column", (), {"name": "reviewed_at"})(),
        type("Column", (), {"name": "created_at"})(),
        type("Column", (), {"name": "updated_at"})(),
    ]

    cursor.fetchall.return_value = [
        (
            "case-1",
            "order-1",
            0.85,
            "TRUE_FRAUD",
            "TRUE_FRAUD",
            None,
            START_DATE,
            END_DATE,
        )
    ]

    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor

    db_context = MagicMock()
    db_context.__enter__.return_value = connection
    db_context.__exit__.return_value = False

    with patch(
        "app.repositories.fraud_weekly_summary_repository.get_db",
        return_value=db_context,
    ):
        cases = repository.get_cases_between(
            START_DATE,
            END_DATE,
        )

    assert len(cases) == 1

    assert cases[0]["id"] == "case-1"
    assert cases[0]["order_id"] == "order-1"
    assert cases[0]["fraud_score"] == 0.85
    assert cases[0]["status"] == "TRUE_FRAUD"
    assert cases[0]["reviewer_decision"] == "TRUE_FRAUD"
    assert cases[0]["reviewed_at"] is None
    assert cases[0]["created_at"] == START_DATE
    assert cases[0]["updated_at"] == END_DATE

    cursor.execute.assert_called_once_with(
        """
                    SELECT
                        id,
                        order_id,
                        fraud_score,
                        status,
                        reviewer_decision,
                        reviewed_at,
                        created_at,
                        updated_at
                    FROM fraud_cases
                    WHERE created_at >= %s
                      AND created_at <= %s
                    ORDER BY created_at ASC
                    """,
        (START_DATE, END_DATE),
    )