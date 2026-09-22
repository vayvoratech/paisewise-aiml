from pathlib import Path
import sys


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LLM_COST_MANAGEMENT_PATH = (
    PROJECT_ROOT / "llm_cost_management"
)

AI_QUALITY_MONITORING_PATH = (
    PROJECT_ROOT / "ai_quality_monitoring"
)


# --------------------------------------------------
# Add project folders to Python path
# --------------------------------------------------

sys.path.insert(
    0,
    str(LLM_COST_MANAGEMENT_PATH)
)

sys.path.insert(
    0,
    str(AI_QUALITY_MONITORING_PATH)
)


# --------------------------------------------------
# Task 1 - LLM Cost Management
# --------------------------------------------------

from cost_manager import CostManager
from llm_service import LLMService


# --------------------------------------------------
# Task 2 - AI Quality Monitoring
# --------------------------------------------------

from quality_evaluator import QualityEvaluator
from quality_tracker import QualityTracker
from quality_storage import QualityStorage
from quality_gate import QualityGate


class AIMonitoring:

    def __init__(self):

        # --------------------------------------------------
        # Task 1
        # --------------------------------------------------

        self.cost_manager = CostManager()

        self.llm_service = LLMService()

        # --------------------------------------------------
        # Task 2
        #
        # IMPORTANT:
        # Use the same CostManager and LLMService
        # inside QualityEvaluator.
        # --------------------------------------------------

        self.quality_evaluator = QualityEvaluator(
            cost_manager=self.cost_manager,
            llm_service=self.llm_service
        )

        self.quality_tracker = QualityTracker()

        self.quality_storage = QualityStorage()

        self.quality_gate = QualityGate()


    def evaluate_response(
        self,
        feature,
        prompt,
        response,
        user_id=None,
        response_id=None
    ):
        """
        Evaluate an existing PaiseWise API response
        using the Task 2 quality monitoring system.

        The Gemini evaluation itself is tracked by
        Task 1 CostManager.
        """

        evaluation = self.quality_evaluator.evaluate(
            feature=feature,
            prompt=prompt,
            response=response,
            user_id=user_id
        )

        record = self.quality_storage.add_evaluation(
            evaluation=evaluation,
            quality_tracker=self.quality_tracker,
            user_id=user_id,
            response_id=response_id
        )

        gate_result = self.quality_gate.evaluate(
            feature=feature,
            score=evaluation["score"]
        )

        return {
            "evaluation": evaluation,
            "quality_record": record,
            "quality_gate": gate_result
        }


    def generate_with_cost_tracking(
        self,
        user_id,
        user_tier,
        feature,
        prompt,
        input_cost_per_1k,
        output_cost_per_1k
    ):
        """
        Make a real Gemini request through Task 1
        CostManager and return cost information.

        This method is kept for direct Task 1 usage
        outside the quality-monitoring flow.
        """

        result = self.cost_manager.process_llm_request(
            user_id=user_id,
            user_tier=user_tier,
            feature=feature,
            llm_service=self.llm_service,
            prompt=prompt,
            input_cost_per_1k=input_cost_per_1k,
            output_cost_per_1k=output_cost_per_1k
        )

        return result


# --------------------------------------------------
# Test AI Monitoring
# --------------------------------------------------

if __name__ == "__main__":

    monitoring = AIMonitoring()

    test_prompt = (
        "What is diversification in investing?"
    )

    test_response = (
        "Diversification means spreading investments "
        "across different assets or sectors to reduce "
        "the impact of poor performance in one investment."
    )

    result = monitoring.evaluate_response(
        feature="ask",
        prompt=test_prompt,
        response=test_response,
        user_id="TEST_USER",
        response_id="TEST_RESPONSE"
    )

    print("=" * 60)
    print("AI MONITORING TEST")
    print("=" * 60)

    print("\nFeature:")
    print(
        result["evaluation"]["feature"]
    )

    print("\nQuality Score:")
    print(
        result["evaluation"]["score"],
        "/ 5"
    )

    print("\nReason:")
    print(
        result["evaluation"]["reason"]
    )

    print("\nModel:")
    print(
        result["evaluation"]["model"]
    )

    print("\nCost Tracking:")

    cost_tracking = result["evaluation"].get(
        "cost_tracking",
        {}
    )

    print(
        "Cached:",
        cost_tracking.get("cached")
    )

    print(
        "Input Tokens:",
        cost_tracking.get("input_tokens")
    )

    print(
        "Output Tokens:",
        cost_tracking.get("output_tokens")
    )

    print(
        "Thinking Tokens:",
        cost_tracking.get("thinking_tokens")
    )

    print(
        "Billable Output Tokens:",
        cost_tracking.get(
            "billable_output_tokens"
        )
    )

    print(
        "Total Tokens:",
        cost_tracking.get(
            "total_tokens"
        )
    )

    print(
        "Cost:",
        cost_tracking.get("cost_inr"),
        "INR"
    )

    print(
        "Total Cost:",
        cost_tracking.get(
            "total_cost"
        ),
        "INR"
    )

    print(
        "Remaining Budget:",
        cost_tracking.get(
            "remaining_budget"
        ),
        "INR"
    )

    print(
        "Alerts:",
        cost_tracking.get(
            "alerts"
        )
    )

    print("\nQuality Gate:")
    print(
        result["quality_gate"]["status"]
    )

    print("\nAlert:")
    print(
        result["quality_gate"]["alert"]
    )

    print("\nFallback:")
    print(
        result["quality_gate"]["fallback"]
    )

    print("\nQuality Record:")
    print(
        result["quality_record"]
    )

    print("=" * 60)