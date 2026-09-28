from datetime import datetime, timezone

import pytest

from app.services.llm_cost_service import (
    LLMCostService,
)


def test_record_usage():
    service = LLMCostService(
        input_cost_per_million=1.0,
        output_cost_per_million=2.0,
    )

    timestamp = datetime(
        2026,
        9,
        16,
        10,
        0,
        tzinfo=timezone.utc,
    )

    record = service.record_usage(
        model="test-model",
        prompt_tokens=1000,
        completion_tokens=500,
        thoughts_tokens=100,
        tool_use_prompt_tokens=50,
        recorded_at=timestamp,
    )

    assert record.model == "test-model"
    assert record.prompt_tokens == 1000
    assert record.completion_tokens == 500
    assert record.thoughts_tokens == 100
    assert record.tool_use_prompt_tokens == 50
    assert record.total_tokens == 1650
    assert record.recorded_at == timestamp


def test_calculate_cost():
    service = LLMCostService(
        input_cost_per_million=1.0,
        output_cost_per_million=2.0,
    )

    record = service.record_usage(
        model="test-model",
        prompt_tokens=1_000_000,
        completion_tokens=500_000,
    )

    cost = service.calculate_cost(record)

    assert cost == pytest.approx(2.0)


def test_usage_records_are_stored():
    service = LLMCostService(
        input_cost_per_million=1.0,
        output_cost_per_million=2.0,
    )

    service.record_usage(
        model="test-model",
        prompt_tokens=100,
        completion_tokens=50,
    )

    records = service.get_usage_records()

    assert len(records) == 1
    assert records[0].total_tokens == 150


def test_negative_token_count_rejected():
    service = LLMCostService(
        input_cost_per_million=1.0,
        output_cost_per_million=2.0,
    )

    with pytest.raises(
        ValueError,
        match="prompt_tokens cannot be negative",
    ):
        service.record_usage(
            model="test-model",
            prompt_tokens=-1,
            completion_tokens=100,
        )


def test_empty_model_rejected():
    service = LLMCostService(
        input_cost_per_million=1.0,
        output_cost_per_million=2.0,
    )

    with pytest.raises(
        ValueError,
        match="model cannot be empty",
    ):
        service.record_usage(
            model="",
            prompt_tokens=100,
            completion_tokens=50,
        )