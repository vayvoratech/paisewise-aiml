from llm_cost_tracker import LLMCostTracker
from budget_monitor import BudgetMonitor
from llm_router import LLMRouter
from cost_storage import CostStorage
from llm_cache import LLMCache


class CostManager:

    def __init__(self):

        self.tracker = LLMCostTracker()
        self.budget_monitor = BudgetMonitor()
        self.router = LLMRouter()
        self.storage = CostStorage()
        self.cache = LLMCache()

    def select_model(
        self,
        user_tier,
        feature
    ):

        return self.router.select_model(
            user_tier,
            feature
        )

    def process_llm_request(
        self,
        user_id,
        user_tier,
        feature,
        llm_service,
        prompt,
        input_cost_per_1k,
        output_cost_per_1k
    ):

        # -------------------------------------------------
        # 1. Select model based on user tier and feature
        # -------------------------------------------------

        model = self.select_model(
            user_tier,
            feature
        )

        # -------------------------------------------------
        # 2. Check cache
        # -------------------------------------------------

        cached_response = self.cache.get(prompt)

        if cached_response is not None:

            return {
                "response": cached_response,
                "model": model,
                "input_tokens": 0,
                "output_tokens": 0,
                "thinking_tokens": 0,
                "billable_output_tokens": 0,
                "total_tokens": 0,
                "cost_inr": 0,
                "cached": True,
                "alerts": [],
                "total_cost": self.tracker.get_total_cost(),
                "remaining_budget": (
                    self.budget_monitor.get_remaining_budget()
                )
            }

        # -------------------------------------------------
        # 3. Call Gemini / LLM service
        # -------------------------------------------------

        llm_result = llm_service.generate_response(
            prompt=prompt,
            model=model
        )

        # -------------------------------------------------
        # 4. Store response in cache
        # -------------------------------------------------

        self.cache.set(
            prompt,
            llm_result["response"]
        )

        # -------------------------------------------------
        # 5. Read token usage
        # -------------------------------------------------

        input_tokens = llm_result["input_tokens"]

        output_tokens = llm_result["output_tokens"]

        thinking_tokens = llm_result.get(
            "thinking_tokens",
            0
        )

        total_tokens = llm_result.get(
            "total_tokens",
            input_tokens
            + output_tokens
            + thinking_tokens
        )

        # -------------------------------------------------
        # 6. Calculate billable output tokens
        #
        # Gemini billing includes thinking tokens
        # along with output tokens.
        # -------------------------------------------------

        billable_output_tokens = (
            output_tokens
            + thinking_tokens
        )

        # -------------------------------------------------
        # 7. Calculate LLM cost
        # -------------------------------------------------

        cost = self.tracker.calculate_cost(
            input_tokens,
            billable_output_tokens,
            input_cost_per_1k,
            output_cost_per_1k
        )

        # -------------------------------------------------
        # 8. Track usage
        # -------------------------------------------------

        record = self.tracker.track_usage(
            user_id=user_id,
            user_tier=user_tier,
            feature=feature,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thinking_tokens=thinking_tokens,
            cost_inr=cost
        )

        # -------------------------------------------------
        # 9. Save usage record
        # -------------------------------------------------

        self.storage.add_record(
            record
        )

        # -------------------------------------------------
        # 10. Check daily budget
        # -------------------------------------------------

        alerts = self.budget_monitor.add_cost(
            cost
        )

        # -------------------------------------------------
        # 11. Return complete result
        # -------------------------------------------------

        return {
            "response": llm_result["response"],
            "model": model,

            "input_tokens": input_tokens,

            "output_tokens": output_tokens,

            "thinking_tokens": thinking_tokens,

            "billable_output_tokens": (
                billable_output_tokens
            ),

            "total_tokens": total_tokens,

            "cost_inr": cost,

            "cached": False,

            "alerts": alerts,

            "total_cost": (
                self.tracker.get_total_cost()
            ),

            "remaining_budget": (
                self.budget_monitor.get_remaining_budget()
            )
        }