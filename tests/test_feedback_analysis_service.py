
import json

import pytest

from app.services.feedback_analysis_service import FeedbackAnalysisService


def create_dataset(tmp_path):
    dataset = {
        "dataset_name": "test_dataset",
        "version": "1.0",
        "cases": [
            {
                "id": "TC001",
                "theme": "answer_relevance",
                "question": "What is an ETF?",
                "expected_behavior": "Answer the question directly.",
            },
            {
                "id": "TC002",
                "theme": "topic_understanding",
                "question": "What is a bond?",
                "expected_behavior": "Identify the financial topic.",
            },
        ],
    }

    path = tmp_path / "dataset.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(dataset, file)

    return path


def test_load_cases(tmp_path):
    dataset_path = create_dataset(tmp_path)

    service = FeedbackAnalysisService(dataset_path)

    cases = service.load_cases()

    assert len(cases) == 2
    assert cases[0].case_id == "TC001"
    assert cases[0].theme == "answer_relevance"


def test_get_cases_by_theme(tmp_path):
    dataset_path = create_dataset(tmp_path)

    service = FeedbackAnalysisService(dataset_path)

    cases = service.get_cases_by_theme("answer_relevance")

    assert len(cases) == 1
    assert cases[0].case_id == "TC001"


def test_missing_dataset_raises_error(tmp_path):
    service = FeedbackAnalysisService(
        tmp_path / "missing.json"
    )

    with pytest.raises(FileNotFoundError):
        service.load_cases()


def test_invalid_cases_structure(tmp_path):
    path = tmp_path / "invalid.json"

    path.write_text(
        json.dumps({"cases": "invalid"}),
        encoding="utf-8",
    )

    service = FeedbackAnalysisService(path)

    with pytest.raises(ValueError):
        service.load_cases()
def test_analyze_feedback_dataset_groups_records_by_theme():
    from types import SimpleNamespace

    service = FeedbackAnalysisService("unused.json")

    records = [
        SimpleNamespace(
            record_id="FB001",
            theme="answer_relevance",
            feedback="down",
        ),
        SimpleNamespace(
            record_id="FB002",
            theme="answer_relevance",
            feedback="up",
        ),
        SimpleNamespace(
            record_id="FB003",
            theme="topic_understanding",
            feedback="down",
        ),
    ]

    analysis = service.analyze_feedback_dataset(records)

    assert analysis["answer_relevance"]["total"] == 2
    assert analysis["answer_relevance"]["up"] == 1
    assert analysis["answer_relevance"]["down"] == 1
    assert analysis["answer_relevance"]["records"] == [
        "FB001",
        "FB002",
    ]

    assert analysis["topic_understanding"]["total"] == 1
    assert analysis["topic_understanding"]["up"] == 0
    assert analysis["topic_understanding"]["down"] == 1
    assert analysis["topic_understanding"]["records"] == ["FB003"]


def test_analyze_feedback_dataset_handles_empty_records():
    service = FeedbackAnalysisService("unused.json")

    analysis = service.analyze_feedback_dataset([])

    assert analysis == {}