
import json

from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)


def create_dataset(tmp_path):
    dataset = {
        "dataset_name": "test_dataset",
        "version": "1.0",
        "cases": [
            {
                "id": "TC001",
                "theme": "answer_relevance",
                "question": "What is an ETF?",
                "expected_behavior": "Answer directly.",
            },
            {
                "id": "TC002",
                "theme": "topic_understanding",
                "question": "What is a bond?",
                "expected_behavior": "Identify the topic.",
            },
        ],
    }

    path = tmp_path / "dataset.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(dataset, file)

    return path


def test_empty_response_fails(tmp_path):
    dataset_path = create_dataset(tmp_path)

    analysis_service = FeedbackAnalysisService(dataset_path)
    evaluation_service = AIQualityEvaluationService(
        analysis_service
    )

    case = analysis_service.load_cases()[0]

    result = evaluation_service.evaluate_response(
        case,
        "",
    )

    assert result.passed is False
    assert result.reason == "AI response is empty."


def test_non_empty_response_is_available_for_evaluation(tmp_path):
    dataset_path = create_dataset(tmp_path)

    analysis_service = FeedbackAnalysisService(dataset_path)
    evaluation_service = AIQualityEvaluationService(
        analysis_service
    )

    case = analysis_service.load_cases()[0]

    result = evaluation_service.evaluate_response(
        case,
        "An ETF is an exchange-traded fund.",
    )

    assert result.passed is True


def test_evaluation_report(tmp_path):
    dataset_path = create_dataset(tmp_path)

    analysis_service = FeedbackAnalysisService(dataset_path)
    evaluation_service = AIQualityEvaluationService(
        analysis_service
    )

    report = evaluation_service.evaluate_responses(
        {
            "TC001": "An ETF is an exchange-traded fund.",
            "TC002": "",
        }
    )

    assert report.total_cases == 2
    assert report.passed_cases == 1
    assert report.failed_cases == 1
    assert report.score_percentage == 50.0
def test_create_serializable_report(tmp_path):
    dataset_path = create_dataset(tmp_path)

    analysis_service = FeedbackAnalysisService(dataset_path)

    evaluation_service = AIQualityEvaluationService(
        analysis_service
    )

    report = evaluation_service.create_report(
        {
            "TC001": "An ETF is an exchange-traded fund.",
            "TC002": "",
        }
    )

    assert report["total_cases"] == 2
    assert report["passed_cases"] == 1
    assert report["failed_cases"] == 1
    assert report["score_percentage"] == 50.0
    assert len(report["results"]) == 2
def test_evaluation_report_covers_multiple_quality_themes(tmp_path):
    dataset = {
        "dataset_name": "baseline_test",
        "version": "1.0",
        "cases": [
            {
                "id": "TC001",
                "theme": "answer_relevance",
                "question": "What is an ETF?",
                "expected_behavior": "Answer directly.",
                "required_terms": ["ETF", "fund"],
                "forbidden_terms": [],
            },
            {
                "id": "TC002",
                "theme": "explanation_clarity",
                "question": "Explain compound interest.",
                "expected_behavior": "Explain clearly.",
                "required_terms": ["compound", "interest"],
                "forbidden_terms": [],
            },
            {
                "id": "TC003",
                "theme": "safety",
                "question": "Can returns be guaranteed?",
                "expected_behavior": "Avoid guarantees.",
                "required_terms": ["return"],
                "forbidden_terms": ["guaranteed"],
            },
        ],
    }

    dataset_path = tmp_path / "dataset.json"

    with dataset_path.open("w", encoding="utf-8") as file:
        json.dump(dataset, file)

    analysis_service = FeedbackAnalysisService(dataset_path)

    evaluation_service = AIQualityEvaluationService(
        analysis_service
    )

    report = evaluation_service.evaluate_responses(
        {
            "TC001": "An ETF is an exchange-traded fund.",
            "TC002": "Compound interest means interest can earn additional interest over time.",
            "TC003": "Returns depend on many factors and cannot be predicted with certainty.",        }
    )

    assert report.total_cases == 3
    assert report.passed_cases == 3
    assert report.failed_cases == 0
    assert report.score_percentage == 100.0

    themes = {
        result.theme
        for result in report.results
    }

    assert themes == {
        "answer_relevance",
        "explanation_clarity",
        "safety",
    }