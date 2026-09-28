from dataclasses import asdict, dataclass

from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)


@dataclass(frozen=True)
class ABTestResult:
    """Represents an A/B evaluation comparison."""

    case_id: str
    theme: str
    variant_a_passed: bool
    variant_b_passed: bool


@dataclass(frozen=True)
class ABTestReport:
    """Represents aggregate A/B evaluation results."""

    total_cases: int
    variant_a_passed: int
    variant_b_passed: int
    variant_a_score: float
    variant_b_score: float
    results: list[ABTestResult]


class AIABTestService:
    """Compares two AI response variants using the same evaluation cases."""

    def __init__(
        self,
        feedback_analysis_service: FeedbackAnalysisService,
        quality_evaluation_service: AIQualityEvaluationService,
    ) -> None:
        self.feedback_analysis_service = feedback_analysis_service
        self.quality_evaluation_service = quality_evaluation_service

    def evaluate(
        self,
        variant_a: dict[str, str],
        variant_b: dict[str, str],
        themes: list[str],
        available_context: dict[str, object] | None = None,
    ) -> ABTestReport:
        """
        Evaluate two variants for the configured improvement themes.

        available_context is optional so existing callers remain
        backward compatible.
        """

        normalized_themes = {
            theme.strip().lower()
            for theme in themes
            if isinstance(theme, str) and theme.strip()
        }

        cases = [
            case
            for case in self.feedback_analysis_service.load_cases()
            if case.theme.lower() in normalized_themes
        ]

        results: list[ABTestResult] = []

        for case in cases:
            result_a = self.quality_evaluation_service.evaluate_response(
                case=case,
                response=variant_a.get(case.case_id, ""),
                available_context=available_context,
            )

            result_b = self.quality_evaluation_service.evaluate_response(
                case=case,
                response=variant_b.get(case.case_id, ""),
                available_context=available_context,
            )

            results.append(
                ABTestResult(
                    case_id=case.case_id,
                    theme=case.theme,
                    variant_a_passed=result_a.passed,
                    variant_b_passed=result_b.passed,
                )
            )

        total_cases = len(results)

        variant_a_passed = sum(
            result.variant_a_passed
            for result in results
        )

        variant_b_passed = sum(
            result.variant_b_passed
            for result in results
        )

        variant_a_score = (
            variant_a_passed / total_cases * 100
            if total_cases
            else 0.0
        )

        variant_b_score = (
            variant_b_passed / total_cases * 100
            if total_cases
            else 0.0
        )

        return ABTestReport(
            total_cases=total_cases,
            variant_a_passed=variant_a_passed,
            variant_b_passed=variant_b_passed,
            variant_a_score=variant_a_score,
            variant_b_score=variant_b_score,
            results=results,
        )

    def evaluate_feedback_records(
        self,
        variant_a: dict[str, str],
        variant_b: dict[str, str],
        feedback_records,
        available_context: dict[str, object] | None = None,
    ) -> ABTestReport:
        """
        Evaluate variants for themes represented by feedback records.

        Feedback records are expected to come from FeedbackDatasetService.
        This method does not persist or modify feedback data.

        available_context is optional and is forwarded to the existing
        quality evaluator when personalization requirements need context.
        """

        themes = sorted(
            {
                record.theme
                for record in feedback_records
                if isinstance(record.theme, str)
                and record.theme.strip()
            }
        )

        return self.evaluate(
            variant_a=variant_a,
            variant_b=variant_b,
            themes=themes,
            available_context=available_context,
        )

    def create_report(
        self,
        variant_a: dict[str, str],
        variant_b: dict[str, str],
        themes: list[str],
        available_context: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Create a JSON-serializable A/B evaluation report."""

        report = self.evaluate(
            variant_a=variant_a,
            variant_b=variant_b,
            themes=themes,
            available_context=available_context,
        )

        return {
            "total_cases": report.total_cases,
            "variant_a": {
                "passed_cases": report.variant_a_passed,
                "score_percentage": report.variant_a_score,
            },
            "variant_b": {
                "passed_cases": report.variant_b_passed,
                "score_percentage": report.variant_b_score,
            },
            "results": [
                asdict(result)
                for result in report.results
            ],
        }