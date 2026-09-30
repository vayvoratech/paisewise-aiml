from unittest.mock import Mock

from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm_cost_service import LLMCostService


def test_gemini_provider_records_usage():
    cost_service = LLMCostService(
        input_cost_per_million=0.30,
        output_cost_per_million=2.50,
    )

    provider = GeminiProvider.__new__(GeminiProvider)
    provider.model = "test-model"
    provider.cost_service = cost_service

    response = Mock()
    response.usage_metadata = Mock(
        prompt_token_count=100,
        candidates_token_count=50,
        thoughts_token_count=20,
        tool_use_prompt_token_count=10,
        total_token_count=180,
    )

    provider._record_usage(response)

    records = cost_service.get_usage_records()

    assert len(records) == 1

    record = records[0]

    assert record.model == "test-model"
    assert record.prompt_tokens == 100
    assert record.completion_tokens == 50
    assert record.thoughts_tokens == 20
    assert record.tool_use_prompt_tokens == 10
    assert record.total_tokens == 180