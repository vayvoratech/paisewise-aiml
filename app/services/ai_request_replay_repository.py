from datetime import datetime
from typing import Any

from psycopg.types.json import Jsonb

from app.db.session import get_db


class AIRequestReplayRepository:
    """Persists AI request replay records in PostgreSQL."""

    def create_request(
        self,
        request_id: str,
        service_name: str,
        model: str,
        inputs: Any,
        recorded_at: datetime,
    ) -> dict[str, Any]:
        """Store an AI request and return the persisted record."""

        query = """
            INSERT INTO public.ai_request_replays (
                request_id,
                service_name,
                model,
                inputs,
                recorded_at
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING
                id,
                request_id,
                service_name,
                model,
                inputs,
                recorded_at,
                created_at
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        request_id,
                        service_name,
                        model,
                        Jsonb(inputs),
                        recorded_at,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise RuntimeError(
                        "Failed to create AI request replay record"
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))

    def get_request(
        self,
        request_id: str,
    ) -> dict[str, Any]:
        """Retrieve a persisted AI request by request ID."""

        query = """
            SELECT
                id,
                request_id,
                service_name,
                model,
                inputs,
                recorded_at,
                created_at
            FROM public.ai_request_replays
            WHERE request_id = %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (request_id,))

                row = cursor.fetchone()

                if row is None:
                    raise ValueError(
                        f"AI request replay not found: {request_id}"
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))