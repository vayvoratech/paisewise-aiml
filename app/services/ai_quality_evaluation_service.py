from dataclasses import dataclass
import re

from app.services.feedback_analysis_service import (
    EvaluationCase,
    FeedbackAnalysisService,
)


@dataclass(frozen=True)
class EvaluationResult:
    """Represents the evaluation result for one AI response."""

    case_id: str
    theme: str
    passed: bool
    reason: str


@dataclass(frozen=True)
class EvaluationReport:
    """Represents the aggregate result of an evaluation run."""

    total_cases: int
    passed_cases: int
    failed_cases: int
    score_percentage: float
    results: list[EvaluationResult]


class AIQualityEvaluationService:
    """Evaluates AI responses against the versioned evaluation dataset."""

    def __init__(
        self,
        feedback_analysis_service: FeedbackAnalysisService,
    ) -> None:
        self.feedback_analysis_service = feedback_analysis_service

    @staticmethod
    def _unique_words(text: str) -> set[str]:
        """Return normalized unique words from a response."""

        return set(
            re.findall(
                r"\b[\w'-]+\b",
                text.lower(),
            )
        )

    def _has_meaningful_content(
        self,
        case: EvaluationCase,
        response: str,
    ) -> bool:
        """Check that the response contains content beyond required keywords."""

        response_words = self._unique_words(response)

        required_words: set[str] = set()

        for term in case.required_terms:
            required_words.update(
                self._unique_words(term)
            )

        return len(response_words) > len(required_words)

    @staticmethod
    def _personalization_context_is_supported(
        case: EvaluationCase,
        response: str,
        available_context: dict[str, object] | None,
    ) -> bool:
        """Verify personalization requirements when context is supplied."""

        requirements = case.personalization_requirements

        if not requirements.get("requires_available_context", False):
            return True

        if available_context is None:
            return False

        if not available_context:
            return False

        response_words = AIQualityEvaluationService._unique_words(
            response
        )

        context_text = " ".join(
            str(value)
            for value in available_context.values()
            if value is not None
        )

        context_words = AIQualityEvaluationService._unique_words(
            context_text
        )

        return bool(
            response_words.intersection(context_words)
        )

    @staticmethod
    def _classification_is_valid(
        case: EvaluationCase,
        response: str,
    ) -> bool:
        """Validate classification responses using dataset configuration."""

        requirements = case.classification_requirements

        if not requirements:
            return True

        allowed_values = requirements.get("allowed_values", [])

        if not isinstance(allowed_values, list):
            return False

        normalized_allowed_values = {
            str(value).strip().lower()
            for value in allowed_values
            if str(value).strip()
        }

        if not normalized_allowed_values:
            return False

        response_words = AIQualityEvaluationService._unique_words(
            response
        )

        matched_values = (
            normalized_allowed_values.intersection(response_words)
        )

        if requirements.get("exactly_one", False):
            return len(matched_values) == 1

        return bool(matched_values)

    def evaluate_response(
        self,
        case: EvaluationCase,
        response: str,
        available_context: dict[str, object] | None = None,
    ) -> EvaluationResult:
        """Evaluate one AI response against its configured criteria."""

        if not response or not response.strip():
            return EvaluationResult(
                case_id=case.case_id,
                theme=case.theme,
                passed=False,
                reason="AI response is empty.",
            )

        normalized_response = response.lower()

        missing_terms = [
            term
            for term in case.required_terms
            if term.lower() not in normalized_response
        ]

        if missing_terms:
            return EvaluationResult(
                case_id=case.case_id,
                theme=case.theme,
                passed=False,
                reason=(
                    "Missing required terms: "
                    + ", ".join(missing_terms)
                ),
            )

        forbidden_terms_found = [
            term
            for term in case.forbidden_terms
            if term.lower() in normalized_response
        ]

        if forbidden_terms_found:
            return EvaluationResult(
                case_id=case.case_id,
                theme=case.theme,
                passed=False,
                reason=(
                    "Forbidden terms found: "
                    + ", ".join(forbidden_terms_found)
                ),
            )

        if not self._has_meaningful_content(
            case=case,
            response=response,
        ):
            return EvaluationResult(
                case_id=case.case_id,
                theme=case.theme,
                passed=False,
                reason=(
                    "Response contains required terms but does not "
                    "contain enough additional meaningful content."
                ),
            )

        if not self._personalization_context_is_supported(
            case=case,
            response=response,
            available_context=available_context,
        ):
            return EvaluationResult(
                case_id=case.case_id,
                theme=case.theme,
                passed=False,
                reason=(
                    "Personalized response requires explicitly "
                    "available user context."
                ),
            )

        if not self._classification_is_valid(
            case=case,
            response=response,
        ):
            return EvaluationResult(
                case_id=case.case_id,
                theme=case.theme,
                passed=False,
                reason=(
                    "Response does not contain exactly one valid "
                    "classification value from the configured "
                    "evaluation criteria."
                ),
            )

        return EvaluationResult(
            case_id=case.case_id,
            theme=case.theme,
            passed=True,
            reason="Response satisfies configured evaluation criteria.",
        )

    def create_report(
        self,
        responses: dict[str, str],
    ) -> dict[str, object]:
        """Create a serializable evaluation report."""

        report = self.evaluate_responses(responses)

        return {
            "total_cases": report.total_cases,
            "passed_cases": report.passed_cases,
            "failed_cases": report.failed_cases,
            "score_percentage": report.score_percentage,
            "results": [
                {
                    "case_id": result.case_id,
                    "theme": result.theme,
                    "passed": result.passed,
                    "reason": result.reason,
                }
                for result in report.results
            ],
        }

    def evaluate_responses(
        self,
        responses: dict[str, str],
    ) -> EvaluationReport:
        """Evaluate responses for all cases in the configured dataset."""

        cases = self.feedback_analysis_service.load_cases()

        results = [
            self.evaluate_response(
                case=case,
                response=responses.get(case.case_id, ""),
            )
            for case in cases
        ]

        passed_cases = sum(
            1
            for result in results
            if result.passed
        )

        total_cases = len(results)
        failed_cases = total_cases - passed_cases

        score_percentage = (
            (passed_cases / total_cases) * 100
            if total_cases
            else 0.0
        )

        return EvaluationReport(
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            score_percentage=score_percentage,
            results=results,
        )