from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)


def test_insufficient_knowledge_rejects_unsupported_future_claim():
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
        if case.case_id == "TC008"
    )

    response = (
        "The stock price will be 500 next month."
    )

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
    )

    assert result.passed is False

def test_insufficient_knowledge_accepts_uncertain_response():
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
        if case.case_id == "TC008"
    )

    response = (
        "A specific stock's price next month cannot be known "
        "with certainty from the available information. "
        "Future prices depend on changing market conditions."
    )

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
    )

    assert result.passed is True