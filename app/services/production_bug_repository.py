from datetime import datetime
from typing import Any

from app.db.session import get_db


class ProductionBugRepository:
    """Persists and retrieves production bug records from PostgreSQL."""

    def create_bug(
        self,
        bug_id: str,
        service_name: str,
        severity: str,
        description: str,
        detected_at: datetime,
    ) -> dict[str, Any]:
        """Create a production bug record."""

        query = """
            INSERT INTO public.production_bugs (
                bug_id,
                service_name,
                severity,
                description,
                detected_at
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING
                id,
                bug_id,
                service_name,
                severity,
                description,
                detected_at,
                resolved_at,
                created_at
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        bug_id,
                        service_name,
                        severity,
                        description,
                        detected_at,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise RuntimeError(
                        "Failed to create production bug"
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))

    def resolve_bug(
        self,
        bug_id: str,
        resolved_at: datetime,
    ) -> dict[str, Any]:
        """Record the resolution time for a production bug."""

        query = """
            UPDATE public.production_bugs
            SET resolved_at = %s
            WHERE bug_id = %s
            RETURNING
                id,
                bug_id,
                service_name,
                severity,
                description,
                detected_at,
                resolved_at,
                created_at
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        resolved_at,
                        bug_id,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise ValueError(
                        f"Production bug not found: {bug_id}"
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))

    def get_bug(
        self,
        bug_id: str,
    ) -> dict[str, Any]:
        """Retrieve a production bug by its ID."""

        query = """
            SELECT
                id,
                bug_id,
                service_name,
                severity,
                description,
                detected_at,
                resolved_at,
                created_at
            FROM public.production_bugs
            WHERE bug_id = %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (bug_id,))

                row = cursor.fetchone()

                if row is None:
                    raise ValueError(
                        f"Production bug not found: {bug_id}"
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))