from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)


def test_conversation_continuity_rejects_context_free_response():
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
        if case.case_id == "TC007"
    )

    response = (
        "Compare compare compare."
    )

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
    )

    assert result.passed is False

    
def test_conversation_continuity_accepts_contextual_response():
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
        if case.case_id == "TC007"
    )

    response = (
        "Compared with the investment we discussed earlier, "
        "this investment has different characteristics and "
        "should be considered in the context of our earlier discussion."
    )

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
    )

    assert result.passed is True