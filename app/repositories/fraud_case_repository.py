from typing import Any

from app.db.session import get_db


class FraudCaseRepository:
    def create_case(
        self,
        order_id: str,
        fraud_score: float,
    ) -> dict[str, Any]:
        query = """
            INSERT INTO fraud_cases (
                order_id,
                fraud_score,
                status
            )
            VALUES (%s, %s, 'PENDING_REVIEW')
            RETURNING
                id,
                order_id,
                fraud_score,
                status,
                reviewer_decision,
                reviewed_at,
                created_at,
                updated_at
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (order_id, fraud_score),
                )

                row = cursor.fetchone()
                columns = [desc.name for desc in cursor.description]

                return dict(zip(columns, row))

    def get_case(
        self,
        case_id: str,
    ) -> dict[str, Any] | None:
        query = """
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
            WHERE id = %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (case_id,))
                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [desc.name for desc in cursor.description]

                return dict(zip(columns, row))

    def update_reviewer_decision(
        self,
        case_id: str,
        decision: str,
    ) -> dict[str, Any] | None:
        query = """
            UPDATE fraud_cases
            SET
                reviewer_decision = %s,
                status = %s,
                reviewed_at = NOW(),
                updated_at = NOW()
            WHERE id = %s
            RETURNING
                id,
                order_id,
                fraud_score,
                status,
                reviewer_decision,
                reviewed_at,
                created_at,
                updated_at
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (decision, decision, case_id),
                )

                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [desc.name for desc in cursor.description]

                return dict(zip(columns, row))

    def list_pending_cases(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        query = """
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
            WHERE status = 'PENDING_REVIEW'
            ORDER BY created_at DESC
            LIMIT %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()

                columns = [desc.name for desc in cursor.description]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]