from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app
from app.repositories.fraud_training_repository import (
    FraudTrainingRepository,
)


client = TestClient(app)

REAL_ORDER_ID = "ae55f1d8-e767-4b28-b6a9-2bbe5cf58c80"


def test_real_false_positive_decision_flow():
    case_id = None

    try:
        # Create temporary fraud case directly in PostgreSQL.
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO fraud_cases (
                        order_id,
                        fraud_score,
                        status
                    )
                    VALUES (%s, %s, 'PENDING_REVIEW')
                    RETURNING id
                    """,
                    (REAL_ORDER_ID, 0.85),
                )

                case_id = cursor.fetchone()[0]

        # Send the real API request.
        response = client.post(
            f"/fraud/cases/{case_id}/decision",
            json={"decision": "FALSE_POSITIVE"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["case_id"] == str(case_id)
        assert data["order_id"] == REAL_ORDER_ID
        assert data["decision"] == "FALSE_POSITIVE"
        assert data["status"] == "FALSE_POSITIVE"

        # Verify PostgreSQL state.
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        status,
                        reviewer_decision,
                        reviewed_at
                    FROM fraud_cases
                    WHERE id = %s
                    """,
                    (case_id,),
                )

                row = cursor.fetchone()

        assert row is not None
        assert row[0] == "FALSE_POSITIVE"
        assert row[1] == "FALSE_POSITIVE"
        assert row[2] is not None

        # Verify training repository can now retrieve
        # this reviewed case.
        repository = FraudTrainingRepository()
        cases = repository.get_reviewed_cases()

        matching_cases = [
            case
            for case in cases
            if str(case["fraud_case_id"]) == str(case_id)
        ]

        assert len(matching_cases) == 1
        assert matching_cases[0]["reviewer_decision"] == "FALSE_POSITIVE"

    finally:
        # Always remove the temporary test case.
        if case_id is not None:
            with get_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM fraud_cases
                        WHERE id = %s
                        """,
                        (case_id,),
                    )