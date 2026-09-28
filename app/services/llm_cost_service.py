import os
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from dotenv import load_dotenv

if TYPE_CHECKING:
    from app.services.llm_usage_repository import LLMUsageRepository


load_dotenv()


@dataclass(frozen=True)
class LLMUsageRecord:
    """Token and performance usage recorded for one LLM request."""

    model: str
    prompt_tokens: int
    completion_tokens: int
    thoughts_tokens: int
    tool_use_prompt_tokens: int
    total_tokens: int
    latency_ms: float | None
    recorded_at: datetime


class LLMCostService:
    """Records LLM usage and calculates configured request costs."""

    def __init__(
        self,
        input_cost_per_million: float,
        output_cost_per_million: float,
        daily_budget: float = 0.0,
        usage_repository: "LLMUsageRepository | None" = None,
    ) -> None:
        if input_cost_per_million < 0:
            raise ValueError(
                "input_cost_per_million cannot be negative"
            )

        if output_cost_per_million < 0:
            raise ValueError(
                "output_cost_per_million cannot be negative"
            )

        if daily_budget < 0:
            raise ValueError(
                "daily_budget cannot be negative"
            )

        self.input_cost_per_million = input_cost_per_million
        self.output_cost_per_million = output_cost_per_million
        self.daily_budget = daily_budget
        self.usage_repository = usage_repository

        self._usage_records: list[LLMUsageRecord] = []

    @classmethod
    def from_environment(
        cls,
        usage_repository: "LLMUsageRepository | None" = None,
    ) -> "LLMCostService":
        """Create the cost service using environment configuration."""

        input_cost = float(
            os.getenv(
                "LLM_INPUT_COST_PER_MILLION",
                "0",
            )
        )

        output_cost = float(
            os.getenv(
                "LLM_OUTPUT_COST_PER_MILLION",
                "0",
            )
        )

        daily_budget = float(
            os.getenv(
                "LLM_DAILY_BUDGET",
                "0",
            )
        )

        return cls(
            input_cost_per_million=input_cost,
            output_cost_per_million=output_cost,
            daily_budget=daily_budget,
            usage_repository=usage_repository,
        )

    def record_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        thoughts_tokens: int = 0,
        tool_use_prompt_tokens: int = 0,
        total_tokens: int | None = None,
        latency_ms: float | None = None,
        recorded_at: datetime | None = None,
    ) -> LLMUsageRecord:
        """Record token usage and request performance."""

        if not model or not model.strip():
            raise ValueError("model cannot be empty")

        token_values = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "thoughts_tokens": thoughts_tokens,
            "tool_use_prompt_tokens": tool_use_prompt_tokens,
        }

        for name, value in token_values.items():
            if value < 0:
                raise ValueError(
                    f"{name} cannot be negative"
                )

        if latency_ms is not None and latency_ms < 0:
            raise ValueError(
                "latency_ms cannot be negative"
            )

        calculated_total = (
            prompt_tokens
            + completion_tokens
            + thoughts_tokens
            + tool_use_prompt_tokens
        )

        if total_tokens is None:
            total_tokens = calculated_total
        elif total_tokens < 0:
            raise ValueError(
                "total_tokens cannot be negative"
            )

        timestamp = (
            recorded_at
            or datetime.now(timezone.utc)
        )

        record = LLMUsageRecord(
            model=model.strip(),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            thoughts_tokens=thoughts_tokens,
            tool_use_prompt_tokens=tool_use_prompt_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            recorded_at=timestamp,
        )

        self._usage_records.append(record)

        if self.usage_repository is not None:
            cost = self.calculate_cost(record)

            self.usage_repository.save(
                record=record,
                cost=cost,
            )

        return record

    def calculate_cost(
        self,
        record: LLMUsageRecord,
    ) -> float:
        """Calculate cost from recorded input/output token usage."""

        input_cost = (
            record.prompt_tokens / 1_000_000
        ) * self.input_cost_per_million

        output_tokens = (
            record.completion_tokens
            + record.thoughts_tokens
        )

        output_cost = (
            output_tokens / 1_000_000
        ) * self.output_cost_per_million

        return input_cost + output_cost

    def get_daily_cost(
        self,
        target_date: date | None = None,
    ) -> float:
        """Return total LLM cost for a UTC calendar date."""

        if target_date is None:
            target_date = datetime.now(
                timezone.utc
            ).date()

        if self.usage_repository is not None:
            return self.usage_repository.get_daily_cost(
                target_date
            )

        total = 0.0

        for record in self._usage_records:
            if record.recorded_at.date() == target_date:
                total += self.calculate_cost(record)

        return total

    def is_daily_budget_exceeded(
        self,
        target_date: date | None = None,
    ) -> bool:
        """Return True when daily cost exceeds the configured budget."""

        if self.daily_budget <= 0:
            return False

        return (
            self.get_daily_cost(target_date)
            > self.daily_budget
        )

    def get_usage_records(
        self,
    ) -> list[LLMUsageRecord]:
        """Return recorded usage records."""

        return list(self._usage_records)