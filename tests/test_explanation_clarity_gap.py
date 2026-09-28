from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)


def test_explanation_clarity_rejects_keyword_only_response():
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
        if case.case_id == "TC004"
    )

    response = "compound interest"

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
    )

    assert result.passed is False


def test_explanation_clarity_accepts_plain_language_response():
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
        if case.case_id == "TC004"
    )

    response = (
        "Compound interest means you earn interest not only "
        "on the money you initially invest, but also on the "
        "interest that has already been added."
    )

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
    )

    assert result.passed is True