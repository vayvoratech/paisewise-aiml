from dataclasses import dataclass
from typing import Any

from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)


@dataclass(frozen=True)
class QualityBaselineResult:
    case_id: str
    theme: str
    baseline_passed: bool
    improved_passed: bool
    baseline_score: float
    improved_score: float


@dataclass(frozen=True)
class QualityBaselineReport:
    total_cases: int
    baseline_passed: int
    improved_passed: int
    baseline_score: float
    improved_score: float
    score_change: float
    improved_themes: list[str]
    regressed_themes: list[str]
    unchanged_themes: list[str]
    results: list[QualityBaselineResult]


class Task10QualityBaselineService:
    """
    Compares pre-improvement and post-improvement AI quality
    using the same golden-set evaluation criteria.

    This service does not modify the existing quality evaluator
    or feedback-analysis service.
    """

    def __init__(
        self,
        feedback_analysis_service: FeedbackAnalysisService,
        quality_evaluation_service: AIQualityEvaluationService,
    ):
        self.feedback_analysis_service = feedback_analysis_service
        self.quality_evaluation_service = quality_evaluation_service

    def _get_cases(
        self,
        themes: list[str] | None = None,
    ):
        """
        Retrieve golden-set cases through the existing
        FeedbackAnalysisService API.
        """
        if themes is None:
            raise ValueError(
                "themes must be provided for baseline evaluation."
            )

        normalized_themes = {
            theme.strip().lower()
            for theme in themes
            if theme and theme.strip()
        }

        cases = []

        for theme in normalized_themes:
            cases.extend(
                self.feedback_analysis_service.get_cases_by_theme(
                    theme
                )
            )

        unique_cases = {}
        for case in cases:
            unique_cases[case.case_id] = case

        return list(unique_cases.values())

    def evaluate(
        self,
        baseline_responses: dict[str, str],
        improved_responses: dict[str, str],
        themes: list[str] | None = None,
        available_context: dict[str, Any] | None = None,
    ) -> QualityBaselineReport:
        """
        Evaluate baseline and improved responses against the
        same golden-set cases.
        """
        cases = self._get_cases(themes)

        results = []

        for case in cases:
            baseline_response = baseline_responses.get(
                case.case_id,
                "",
            )

            improved_response = improved_responses.get(
                case.case_id,
                "",
            )

            baseline_result = (
                self.quality_evaluation_service.evaluate_response(
                    case=case,
                    response=baseline_response,
                    available_context=available_context,
                )
            )

            improved_result = (
                self.quality_evaluation_service.evaluate_response(
                    case=case,
                    response=improved_response,
                    available_context=available_context,
                )
            )

            results.append(
                QualityBaselineResult(
                    case_id=case.case_id,
                    theme=case.theme,
                    baseline_passed=baseline_result.passed,
                    improved_passed=improved_result.passed,
                    baseline_score=(
                        100.0
                        if baseline_result.passed
                        else 0.0
                    ),
                    improved_score=(
                        100.0
                        if improved_result.passed
                        else 0.0
                    ),
                )
            )

        total_cases = len(results)

        baseline_passed = sum(
            result.baseline_passed
            for result in results
        )

        improved_passed = sum(
            result.improved_passed
            for result in results
        )

        baseline_score = (
            (baseline_passed / total_cases) * 100.0
            if total_cases
            else 0.0
        )

        improved_score = (
            (improved_passed / total_cases) * 100.0
            if total_cases
            else 0.0
        )

        score_change = improved_score - baseline_score

        improved_themes = []
        regressed_themes = []
        unchanged_themes = []

        themes_seen = {
            result.theme
            for result in results
        }

        for theme in sorted(themes_seen):
            theme_results = [
                result
                for result in results
                if result.theme == theme
            ]

            baseline_theme_passed = sum(
                result.baseline_passed
                for result in theme_results
            )

            improved_theme_passed = sum(
                result.improved_passed
                for result in theme_results
            )

            if improved_theme_passed > baseline_theme_passed:
                improved_themes.append(theme)

            elif improved_theme_passed < baseline_theme_passed:
                regressed_themes.append(theme)

            else:
                unchanged_themes.append(theme)

        return QualityBaselineReport(
            total_cases=total_cases,
            baseline_passed=baseline_passed,
            improved_passed=improved_passed,
            baseline_score=baseline_score,
            improved_score=improved_score,
            score_change=score_change,
            improved_themes=improved_themes,
            regressed_themes=regressed_themes,
            unchanged_themes=unchanged_themes,
            results=results,
        )

    def create_report(
        self,
        baseline_responses: dict[str, str],
        improved_responses: dict[str, str],
        themes: list[str] | None = None,
        available_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a JSON-serializable baseline comparison report.
        """
        report = self.evaluate(
            baseline_responses=baseline_responses,
            improved_responses=improved_responses,
            themes=themes,
            available_context=available_context,
        )

        return {
            "total_cases": report.total_cases,
            "baseline": {
                "passed_cases": report.baseline_passed,
                "score_percentage": report.baseline_score,
            },
            "improved": {
                "passed_cases": report.improved_passed,
                "score_percentage": report.improved_score,
            },
            "score_change": report.score_change,
            "improved_themes": report.improved_themes,
            "regressed_themes": report.regressed_themes,
            "unchanged_themes": report.unchanged_themes,
            "results": [
                {
                    "case_id": result.case_id,
                    "theme": result.theme,
                    "baseline_passed": result.baseline_passed,
                    "improved_passed": result.improved_passed,
                    "baseline_score": result.baseline_score,
                    "improved_score": result.improved_score,
                }
                for result in report.results
            ],
        }