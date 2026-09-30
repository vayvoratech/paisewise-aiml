import pytest

from app.repositories.fraud_case_repository import FraudCaseRepository
from app.db.session import get_db


REAL_ORDER_ID = "ae55f1d8-e767-4b28-b6a9-2bbe5cf58c80"


def test_create_get_update_and_list_fraud_case():
    repository = FraudCaseRepository()
    created = None

    # Ensure this test starts with a clean state.
    with get_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM fraud_cases
                WHERE order_id = %s
                """,
                (REAL_ORDER_ID,),
            )

    try:
        created = repository.create_case(
            order_id=REAL_ORDER_ID,
            fraud_score=0.85,
        )

        assert str(created["order_id"]) == REAL_ORDER_ID
        assert float(created["fraud_score"]) == 0.85
        assert created["status"] == "PENDING_REVIEW"
        assert created["reviewer_decision"] is None

        fetched = repository.get_case(
            created["id"]
        )

        assert fetched is not None
        assert str(fetched["id"]) == str(created["id"])
        assert str(fetched["order_id"]) == REAL_ORDER_ID

        updated = repository.update_reviewer_decision(
            created["id"],
            "FALSE_POSITIVE",
        )

        assert updated is not None
        assert updated["status"] == "FALSE_POSITIVE"
        assert updated["reviewer_decision"] == "FALSE_POSITIVE"
        assert updated["reviewed_at"] is not None

        pending_cases = repository.list_pending_cases()

        assert all(
            case["status"] == "PENDING_REVIEW"
            for case in pending_cases
        )

    finally:
        # Always remove the temporary test record.
        if created is not None:
            with get_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM fraud_cases
                        WHERE id = %s
                        """,
                        (created["id"],),
                    )