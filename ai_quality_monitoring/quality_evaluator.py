import json
import re
import sys
from pathlib import Path


# ==================================================
# Project Paths
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LLM_COST_MANAGEMENT_PATH = (
    PROJECT_ROOT / "llm_cost_management"
)


# ==================================================
# Add LLM Cost Management Path
# ==================================================

sys.path.insert(
    0,
    str(LLM_COST_MANAGEMENT_PATH)
)


# ==================================================
# Task 1 - LLM Cost Management
# ==================================================

from cost_manager import CostManager
from llm_service import LLMService
from pricing_config import (
    GEMINI_INPUT_INR_PER_1K,
    GEMINI_OUTPUT_INR_PER_1K
)


# ==================================================
# Quality Evaluator
# ==================================================

class QualityEvaluator:
    """
    Evaluates the quality of a PaiseWise AI response
    using Gemini as the evaluator.

    Task 1 integration:
    The Gemini evaluation request is sent through
    CostManager so token usage and INR cost are tracked.

    The evaluator supports:

    1. Natural-language AI responses
    2. Structured API responses such as JSON
    """

    def __init__(
        self,
        cost_manager=None,
        llm_service=None
    ):
        """
        Initialize the quality evaluator.

        If CostManager and LLMService are provided,
        they are reused.

        This allows AIMonitoring to share the same
        Task 1 cost-management system.
        """

        self.cost_manager = (
            cost_manager
            if cost_manager is not None
            else CostManager()
        )

        self.llm_service = (
            llm_service
            if llm_service is not None
            else LLMService()
        )

    # ==================================================
    # Evaluate Response
    # ==================================================

    def evaluate(
        self,
        feature,
        prompt,
        response,
        user_id=None
    ):
        """
        Evaluate an AI response and return a quality
        score from 1 to 5.

        The Gemini request is processed through
        Task 1 CostManager.
        """

        evaluation_prompt = f"""
You are an AI quality evaluator for the PaiseWise
financial education application.

Your task is to evaluate the quality of an AI-generated
response or API-generated result.

The response may be:

- Natural language
- Structured JSON
- A dictionary-like API response
- Numerical analysis
- Financial education content

IMPORTANT:

A structured JSON or API response is NOT automatically
a low-quality response.

Do NOT reduce the score simply because the response
contains JSON, Python dictionary formatting, numbers,
fields, or structured data.

Evaluate the actual information and result provided.

--------------------------------------------------
Feature
--------------------------------------------------

{feature}

--------------------------------------------------
User Prompt
--------------------------------------------------

{prompt}

--------------------------------------------------
AI Response
--------------------------------------------------

{response}

--------------------------------------------------
Evaluation Criteria
--------------------------------------------------

Evaluate the response using these five criteria:

1. Accuracy

   - Are the facts, calculations, values, and results correct?

   - If numerical results are provided, check whether
     they appear logically consistent.

2. Relevance

   - Does the response address the user's request?

   - Does it provide information related to the requested
     PaiseWise feature?

3. Clarity

   - Is the information understandable?

   - For structured API responses, check whether the
     fields and values clearly represent the requested
     result.

   - Do NOT penalize the response simply because it is
     structured data.

4. Completeness

   - Does the response contain the important information
     required for the requested feature?

   - For portfolio analysis, consider values such as
     total portfolio value, sector concentration,
     stock concentration, and diversification score
     when they are available.

5. Safety

   - Is the response appropriate for a financial
     education application?

   - It must not provide unsafe personalized financial
     advice or direct buy/sell recommendations.

--------------------------------------------------
Scoring
--------------------------------------------------

5 = Excellent

    Accurate, relevant, clear, complete, and safe.

4 = Good

    Mostly strong, with only minor improvements needed.

3 = Acceptable

    Useful but has noticeable areas for improvement.

2 = Poor

    Important quality problems are present.

1 = Very poor

    Incorrect, irrelevant, incomplete, or unsafe.

IMPORTANT SCORING RULE:

Do NOT give a low score merely because the response
is JSON or structured API data.

For example, if a portfolio API correctly returns:

- Total portfolio value

- Sector concentration

- Stock concentration

- Diversification score

then evaluate whether those results are correct,
relevant, complete, and safe.

If the API response is technically correct but lacks
additional user-friendly explanation, this should be
treated as a minor limitation rather than an automatic
score of 1 or 2.

Return ONLY valid JSON in exactly this format:

{{
    "score": 1,
    "reason": "Short explanation of the score"
}}
"""

        # --------------------------------------------------
        # Call Gemini through Task 1 CostManager
        # --------------------------------------------------

        cost_result = self.cost_manager.process_llm_request(
            user_id=(
                user_id
                if user_id is not None
                else "quality_monitoring"
            ),
            user_tier="premium",
            feature=f"quality_{feature}",
            llm_service=self.llm_service,
            prompt=evaluation_prompt,
            input_cost_per_1k=GEMINI_INPUT_INR_PER_1K,
            output_cost_per_1k=GEMINI_OUTPUT_INR_PER_1K
        )

        evaluation_text = cost_result["response"]

        # --------------------------------------------------
        # Parse Gemini Evaluation
        # --------------------------------------------------

        evaluation = self._parse_evaluation(
            evaluation_text
        )

        # --------------------------------------------------
        # Validate Score
        # --------------------------------------------------

        score = evaluation.get("score")

        if score is None:
            raise ValueError(
                "Gemini evaluation did not contain a score."
            )

        try:
            score = float(score)
        except (TypeError, ValueError):
            raise ValueError(
                "Gemini returned an invalid quality score."
            )

        # --------------------------------------------------
        # Keep Score Between 1 and 5
        # --------------------------------------------------

        if score < 1:
            score = 1

        if score > 5:
            score = 5

        # --------------------------------------------------
        # Evaluation Result
        # --------------------------------------------------

        return {
            "feature": feature,
            "score": float(score),
            "reason": evaluation.get(
                "reason",
                "No evaluation reason provided."
            ),
            "model": cost_result["model"],

            # Task 1 cost information
            "cost_tracking": {
                "cached": cost_result["cached"],
                "input_tokens": cost_result["input_tokens"],
                "output_tokens": cost_result["output_tokens"],
                "thinking_tokens": cost_result[
                    "thinking_tokens"
                ],
                "billable_output_tokens": cost_result[
                    "billable_output_tokens"
                ],
                "total_tokens": cost_result[
                    "total_tokens"
                ],
                "cost_inr": cost_result["cost_inr"],
                "total_cost": cost_result["total_cost"],
                "remaining_budget": cost_result[
                    "remaining_budget"
                ],
                "alerts": cost_result["alerts"]
            }
        }

    # ==================================================
    # Parse Gemini Evaluation
    # ==================================================

    def _parse_evaluation(
        self,
        text
    ):
        """
        Parse the JSON returned by Gemini.

        Handles both clean JSON and JSON surrounded
        by additional text or markdown.
        """

        text = text.strip()

        # --------------------------------------------------
        # Try direct JSON parsing
        # --------------------------------------------------

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # --------------------------------------------------
        # Remove Markdown Code Fence
        # --------------------------------------------------

        cleaned_text = re.sub(
            r"```json\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        cleaned_text = re.sub(
            r"```\s*",
            "",
            cleaned_text
        )

        cleaned_text = cleaned_text.strip()

        try:
            return json.loads(
                cleaned_text
            )
        except json.JSONDecodeError:
            pass

        # --------------------------------------------------
        # Find JSON Object Inside Text
        # --------------------------------------------------

        match = re.search(
            r"\{.*\}",
            cleaned_text,
            re.DOTALL
        )

        if not match:
            raise ValueError(
                "Gemini did not return a valid "
                "quality evaluation."
            )

        try:
            return json.loads(
                match.group()
            )
        except json.JSONDecodeError:
            raise ValueError(
                "Could not parse Gemini quality evaluation."
            )


# ==================================================
# Test Quality Evaluator
# ==================================================

if __name__ == "__main__":

    evaluator = QualityEvaluator()

    # --------------------------------------------------
    # Test 1: Natural Language Response
    # --------------------------------------------------

    test_prompt = (
        "What is diversification in investing?"
    )

    test_response = (
        "Diversification means spreading investments "
        "across different assets or sectors to reduce "
        "the impact of poor performance in one investment."
    )

    result = evaluator.evaluate(
        feature="ask",
        prompt=test_prompt,
        response=test_response,
        user_id="QUALITY_TEST_USER"
    )

    print("=" * 60)
    print("QUALITY EVALUATOR + COST TRACKING TEST")
    print("=" * 60)

    print(
        "\nFeature:",
        result["feature"]
    )

    print(
        "\nQuality Score:",
        result["score"],
        "/ 5"
    )

    print(
        "\nReason:",
        result["reason"]
    )

    print(
        "\nModel:",
        result["model"]
    )

    print(
        "\nTask 1 Cost Tracking:"
    )

    print(
        "Cached:",
        result["cost_tracking"]["cached"]
    )

    print(
        "Input Tokens:",
        result["cost_tracking"]["input_tokens"]
    )

    print(
        "Output Tokens:",
        result["cost_tracking"]["output_tokens"]
    )

    print(
        "Thinking Tokens:",
        result["cost_tracking"]["thinking_tokens"]
    )

    print(
        "Billable Output Tokens:",
        result["cost_tracking"][
            "billable_output_tokens"
        ]
    )

    print(
        "Total Tokens:",
        result["cost_tracking"]["total_tokens"]
    )

    print(
        "Cost:",
        result["cost_tracking"]["cost_inr"],
        "INR"
    )

    print(
        "Total Cost:",
        result["cost_tracking"]["total_cost"],
        "INR"
    )

    print(
        "Remaining Budget:",
        result["cost_tracking"][
            "remaining_budget"
        ],
        "INR"
    )

    print(
        "Alerts:",
        result["cost_tracking"]["alerts"]
    )

    print("=" * 60)