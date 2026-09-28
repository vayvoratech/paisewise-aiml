from datetime import date, datetime, timedelta, timezone

from app.db.session import get_db
from app.services.llm_cost_service import LLMUsageRecord


class LLMUsageRepository:
    """Persists LLM usage records in PostgreSQL."""

    def save(
        self,
        record: LLMUsageRecord,
        cost: float,
    ) -> None:
        """Persist one LLM usage record."""

        with get_db() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO llm_usage (
                    model,
                    prompt_tokens,
                    completion_tokens,
                    thoughts_tokens,
                    tool_use_prompt_tokens,
                    total_tokens,
                    cost,
                    latency_ms,
                    recorded_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    record.model,
                    record.prompt_tokens,
                    record.completion_tokens,
                    record.thoughts_tokens,
                    record.tool_use_prompt_tokens,
                    record.total_tokens,
                    cost,
                    record.latency_ms,
                    record.recorded_at,
                ),
            )

    def get_daily_cost(
        self,
        target_date: date,
    ) -> float:
        """Return total LLM cost for a UTC calendar date."""

        start = datetime(
            target_date.year,
            target_date.month,
            target_date.day,
            tzinfo=timezone.utc,
        )

        end = start + timedelta(days=1)

        with get_db() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT COALESCE(SUM(cost), 0)
                FROM llm_usage
                WHERE recorded_at >= %s
                  AND recorded_at < %s
                """,
                (start, end),
            )

            result = cursor.fetchone()

        return float(result[0] or 0.0)

    def get_daily_usage_summary(
        self,
        target_date: date,
    ) -> dict:
        """Return aggregated LLM usage and performance metrics for a UTC date."""

        start = datetime(
            target_date.year,
            target_date.month,
            target_date.day,
            tzinfo=timezone.utc,
        )

        end = start + timedelta(days=1)

        with get_db() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS request_count,
                    COALESCE(SUM(prompt_tokens), 0) AS input_tokens,
                    COALESCE(SUM(completion_tokens), 0) AS output_tokens,
                    COALESCE(SUM(total_tokens), 0) AS total_tokens,
                    COALESCE(SUM(cost), 0) AS total_cost,
                    AVG(latency_ms) AS average_latency_ms,
                    COUNT(DISTINCT model) AS model_count
                FROM llm_usage
                WHERE recorded_at >= %s
                  AND recorded_at < %s
                """,
                (start, end),
            )

            result = cursor.fetchone()

        return {
            "request_count": int(result[0] or 0),
            "input_tokens": int(result[1] or 0),
            "output_tokens": int(result[2] or 0),
            "total_tokens": int(result[3] or 0),
            "total_cost": float(result[4] or 0.0),
            "average_latency_ms": (
                float(result[5]) if result[5] is not None else None
            ),
            "model_count": int(result[6] or 0),
        }