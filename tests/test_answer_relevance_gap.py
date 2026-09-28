from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)


def test_current_evaluator_exposes_answer_relevance_gap():
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
        if case.case_id == "TC001"
    )

    response = "ETF fund ETF fund."

    result = evaluation_service.evaluate_response(
        case=case,
        response=response,
    )

    # assert result.passed is True
    assert result.passed is False
    assert "meaningful content" in result.reason