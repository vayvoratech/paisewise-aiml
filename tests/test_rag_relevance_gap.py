from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)


def test_rag_relevance_rejects_unrelated_keyword_response():
    feedback_service = FeedbackAnalysisService(
        "tests/data/task10_golden_set.json"
    )

    evaluation_service = AIQualityEvaluationService(
        feedback_analysis_service=feedback_service
    )

    cases = feedback_service.load_cases()

    case = next(
        case
        for case in cases
        if case.case_id == "TC003"
    )

    response = (
        "Diversification diversification diversification."
    )

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
    )

    assert result.passed is False

def test_rag_relevance_accepts_meaningful_diversification_response():
    feedback_service = FeedbackAnalysisService(
        "tests/data/task10_golden_set.json"
    )

    evaluation_service = AIQualityEvaluationService(
        feedback_analysis_service=feedback_service
    )

    cases = feedback_service.load_cases()

    case = next(
        case
        for case in cases
        if case.case_id == "TC003"
    )

    response = (
        "Diversification means spreading investments across "
        "different assets or investments to avoid relying on "
        "a single investment."
    )

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
    )

    assert result.passed is True