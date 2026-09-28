from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)


def test_personalization_rejects_invented_profile_information():
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
        if case.case_id == "TC006"
    )

    response = (
        "Your risk tolerance is high, so you should invest "
        "mostly in stocks."
    )

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
    )

    assert result.passed is False
    assert "available user context" in result.reason


def test_personalization_accepts_supported_profile_context():
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
        if case.case_id == "TC006"
    )

    response = (
        "Based on your beginner experience level, "
        "risk tolerance describes how comfortable you "
        "are with changes in investment value."
    )

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
        available_context={
            "experience_level": "beginner",
        },
    )

    assert result.passed is True