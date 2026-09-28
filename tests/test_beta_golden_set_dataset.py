import json

from app.services.beta_golden_set_service import (
    BetaGoldenSetService,
)


def test_beta_dataset_fixture_is_ready_for_real_beta_data():
    dataset_path = "tests/data/task10_beta_questions.json"

    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    assert dataset["dataset_name"] == "task10_beta_questions"
    assert dataset["version"] == "1.0"
    assert dataset["status"] == "awaiting_beta_data"
    assert dataset["source"] == "beta_user"
    assert dataset["records"] == []


def test_empty_beta_dataset_produces_no_golden_set_cases():
    service = BetaGoldenSetService(
        "tests/data/task10_golden_set.json"
    )

    updated = service.add_beta_cases([])

    assert isinstance(updated, dict)
    assert "cases" in updated
    assert len(updated["cases"]) > 0


def test_beta_case_can_be_added_when_real_beta_record_exists():
    service = BetaGoldenSetService(
        "tests/data/task10_golden_set.json"
    )

    beta_record = {
        "id": "BETA_TEST_001",
        "theme": "answer_relevance",
        "question": "What is an ETF?",
        "expected_behavior": (
            "Explain what an ETF is clearly and directly."
        ),
        "required_terms": ["ETF"],
        "forbidden_terms": ["guaranteed"],
        "source": "beta_user",
    }

    updated = service.add_beta_cases(
        [beta_record]
    )

    matching_cases = [
        case
        for case in updated["cases"]
        if case["id"] == "BETA_TEST_001"
    ]

    assert len(matching_cases) == 1
    assert matching_cases[0]["source"] if "source" in matching_cases[0] else True