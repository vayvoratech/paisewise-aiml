from datetime import datetime
from typing import Any

from app.db.session import get_db


class AIPromptRepository:
    """Persists and retrieves versioned AI prompts from PostgreSQL."""

    def create_prompt(
        self,
        prompt_key: str,
        version: int,
        prompt_text: str,
        is_active: bool,
    ) -> dict[str, Any]:
        query = """
            INSERT INTO public.ai_prompts (
                prompt_key,
                version,
                prompt_text,
                is_active
            )
            VALUES (%s, %s, %s, %s)
            RETURNING
                id,
                prompt_key,
                version,
                prompt_text,
                is_active,
                created_at,
                updated_at
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        prompt_key,
                        version,
                        prompt_text,
                        is_active,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise RuntimeError(
                        "Failed to create AI prompt"
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))

    def get_active_prompt(
        self,
        prompt_key: str,
    ) -> dict[str, Any]:
        query = """
            SELECT
                id,
                prompt_key,
                version,
                prompt_text,
                is_active,
                created_at,
                updated_at
            FROM public.ai_prompts
            WHERE prompt_key = %s
              AND is_active = TRUE
            LIMIT 1
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (prompt_key,))

                row = cursor.fetchone()

                if row is None:
                    raise ValueError(
                        f"No active AI prompt found for key: {prompt_key}"
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))

    def get_prompt_version(
        self,
        prompt_key: str,
        version: int,
    ) -> dict[str, Any]:
        query = """
            SELECT
                id,
                prompt_key,
                version,
                prompt_text,
                is_active,
                created_at,
                updated_at
            FROM public.ai_prompts
            WHERE prompt_key = %s
              AND version = %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (prompt_key, version),
                )

                row = cursor.fetchone()

                if row is None:
                    raise ValueError(
                        f"AI prompt version not found: "
                        f"{prompt_key} v{version}"
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))

    def get_next_version(
        self,
        prompt_key: str,
    ) -> int:
        query = """
            SELECT COALESCE(MAX(version), 0) + 1
            FROM public.ai_prompts
            WHERE prompt_key = %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (prompt_key,))
                row = cursor.fetchone()

                return int(row[0])

    def activate_prompt(
        self,
        prompt_key: str,
        version: int,
    ) -> dict[str, Any]:
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE public.ai_prompts
                    SET
                        is_active = FALSE,
                        updated_at = NOW()
                    WHERE prompt_key = %s
                      AND is_active = TRUE
                    """,
                    (prompt_key,),
                )

                cursor.execute(
                    """
                    UPDATE public.ai_prompts
                    SET
                        is_active = TRUE,
                        updated_at = NOW()
                    WHERE prompt_key = %s
                      AND version = %s
                    RETURNING
                        id,
                        prompt_key,
                        version,
                        prompt_text,
                        is_active,
                        created_at,
                        updated_at
                    """,
                    (
                        prompt_key,
                        version,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise ValueError(
                        f"AI prompt version not found: "
                        f"{prompt_key} v{version}"
                    )

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))