from cost_manager import CostManager


class MockLLMService:

    def generate_response(self, prompt, model):

        return {
            "response": "Mock portfolio response",
            "input_tokens": 1500,
            "output_tokens": 500,
            "thinking_tokens": 0,
            "total_tokens": 2000
        }


def test_cost_manager():

    manager = CostManager()

    # -------------------------------------------------
    # 1. Select model
    # -------------------------------------------------

    model = manager.select_model(
        user_tier="premium",
        feature="portfolio"
    )

    print("Selected model:", model)

    assert model is not None

    # -------------------------------------------------
    # 2. Mock LLM service
    # -------------------------------------------------

    llm_service = MockLLMService()

    # -------------------------------------------------
    # 3. Process LLM request
    # -------------------------------------------------

    result = manager.process_llm_request(
        user_id="U001",
        user_tier="premium",
        feature="portfolio",
        llm_service=llm_service,
        prompt="Give a portfolio diversification explanation",
        input_cost_per_1k=0.5,
        output_cost_per_1k=1.5
    )

    # -------------------------------------------------
    # 4. Validate result
    # -------------------------------------------------

    assert result is not None
    assert result["model"] == model
    assert result["input_tokens"] == 1500
    assert result["output_tokens"] == 500
    assert result["thinking_tokens"] == 0
    assert result["billable_output_tokens"] == 500
    assert result["total_tokens"] == 2000
    assert result["cost_inr"] > 0
    assert result["cached"] is False

    print("\nUsage Result:")
    print(result)

    print("\nCost:")
    print(result["cost_inr"])

    print("\nTotal Cost:")
    print(result["total_cost"])

    print("\nRemaining Budget:")
    print(result["remaining_budget"])

    print("\nAlerts:")
    print(result["alerts"])