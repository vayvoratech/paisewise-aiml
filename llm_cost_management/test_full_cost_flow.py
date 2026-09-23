from cost_manager import CostManager
from pricing_config import (
    GEMINI_INPUT_INR_PER_1K,
    GEMINI_OUTPUT_INR_PER_1K,
)


class MockLLMService:

    def __init__(self):
        self.call_count = 0

    def generate_response(self, prompt, model):

        self.call_count += 1

        return {
            "response": "Mock SIP explanation",
            "input_tokens": 100,
            "output_tokens": 200,
            "thinking_tokens": 50,
            "total_tokens": 350,
        }


def test_full_cost_flow():

    manager = CostManager()
    llm = MockLLMService()

    prompt = "Explain SIP in simple terms"

    # ============================================================
    # FIRST REQUEST
    # ============================================================

    result1 = manager.process_llm_request(
        user_id="U005",
        user_tier="premium",
        feature="jargon",
        llm_service=llm,
        prompt=prompt,
        input_cost_per_1k=GEMINI_INPUT_INR_PER_1K,
        output_cost_per_1k=GEMINI_OUTPUT_INR_PER_1K,
    )

    # ============================================================
    # SECOND REQUEST - SAME PROMPT
    # ============================================================

    result2 = manager.process_llm_request(
        user_id="U006",
        user_tier="premium",
        feature="jargon",
        llm_service=llm,
        prompt=prompt,
        input_cost_per_1k=GEMINI_INPUT_INR_PER_1K,
        output_cost_per_1k=GEMINI_OUTPUT_INR_PER_1K,
    )

    # ============================================================
    # VALIDATE FIRST REQUEST
    # ============================================================

    assert result1["response"] == "Mock SIP explanation"
    assert result1["input_tokens"] == 100
    assert result1["output_tokens"] == 200
    assert result1["thinking_tokens"] == 50

    assert result1["billable_output_tokens"] == 250
    assert result1["total_tokens"] == 350

    assert result1["cached"] is False
    assert result1["cost_inr"] > 0

    # ============================================================
    # VALIDATE SECOND REQUEST
    # ============================================================

    assert result2["response"] == "Mock SIP explanation"
    assert result2["cached"] is True

    assert result2["input_tokens"] == 0
    assert result2["output_tokens"] == 0
    assert result2["thinking_tokens"] == 0
    assert result2["billable_output_tokens"] == 0
    assert result2["total_tokens"] == 0

    assert result2["cost_inr"] == 0

    # ============================================================
    # VALIDATE CACHE
    # ============================================================

    # Gemini should have been called only once.
    assert llm.call_count == 1

    # ============================================================
    # VALIDATE TOTAL COST
    # ============================================================

    assert result2["total_cost"] == result1["cost_inr"]

    print("\n========================================")
    print("FULL COST FLOW TEST")
    print("========================================")

    print("First Request Cost:", result1["cost_inr"])
    print("Second Request Cost:", result2["cost_inr"])
    print("First Request Cached:", result1["cached"])
    print("Second Request Cached:", result2["cached"])
    print("LLM Calls:", llm.call_count)
    print("Total Cost:", result2["total_cost"])