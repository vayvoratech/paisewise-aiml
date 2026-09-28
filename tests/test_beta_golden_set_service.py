import json

import pytest

from app.services.beta_golden_set_service import (
    BetaGoldenSetService,
)


GOLDEN_SET_PATH = "tests/data/task10_golden_set.json"


def create_service():
    return BetaGoldenSetService(GOLDEN_SET_PATH)


def test_load_golden_set():
    service = create_service()

    golden_set = service.load_golden_set()

    assert isinstance(golden_set, dict)
    assert "cases" in golden_set
    assert isinstance(golden_set["cases"], list)
    assert len(golden_set["cases"]) > 0


def test_validate_valid_beta_case():
    service = create_service()

    record = {
        "id": "BETA001",
        "theme": "answer_relevance",
        "question": "What is an ETF?",
        "expected_behavior": (
            "Explain what an ETF is clearly and directly."
        ),
        "required_terms": ["ETF"],
        "forbidden_terms": ["guaranteed"],
        "source": "beta_user",
    }

    case = service.validate_beta_case(record)

    assert case.case_id == "BETA001"
    assert case.theme == "answer_relevance"
    assert case.question == "What is an ETF?"
    assert case.required_terms == ["ETF"]
    assert case.forbidden_terms == ["guaranteed"]


def test_validate_rejects_missing_required_field():
    service = create_service()

    record = {
        "id": "BETA002",
        "theme": "answer_relevance",
        "question": "What is an ETF?",
        "required_terms": ["ETF"],
        "forbidden_terms": [],
        "source": "beta_user",
    }

    with pytest.raises(ValueError, match="Missing required fields"):
        service.validate_beta_case(record)


def test_validate_rejects_non_beta_source():
    service = create_service()

    record = {
        "id": "SIM001",
        "theme": "answer_relevance",
        "question": "What is an ETF?",
        "expected_behavior": "Explain the ETF clearly.",
        "required_terms": ["ETF"],
        "forbidden_terms": [],
        "source": "simulated_pre_deployment",
    }

    with pytest.raises(
        ValueError,
        match="source='beta_user'",
    ):
        service.validate_beta_case(record)


def test_validate_rejects_duplicate_case_ids():
    service = create_service()

    records = [
        {
            "id": "BETA003",
            "theme": "answer_relevance",
            "question": "What is an ETF?",
            "expected_behavior": "Explain an ETF.",
            "required_terms": ["ETF"],
            "forbidden_terms": [],
            "source": "beta_user",
        },
        {
            "id": "BETA003",
            "theme": "topic_understanding",
            "question": "What is diversification?",
            "expected_behavior": "Explain diversification.",
            "required_terms": ["diversification"],
            "forbidden_terms": [],
            "source": "beta_user",
        },
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate beta case ID",
    ):
        service.validate_beta_dataset(records)


def test_validate_rejects_invalid_required_terms():
    service = create_service()

    record = {
        "id": "BETA004",
        "theme": "answer_relevance",
        "question": "What is an ETF?",
        "expected_behavior": "Explain an ETF.",
        "required_terms": "ETF",
        "forbidden_terms": [],
        "source": "beta_user",
    }

    with pytest.raises(
        ValueError,
        match="'required_terms' must be a list",
    ):
        service.validate_beta_case(record)


def test_validate_rejects_empty_string_fields():
    service = create_service()

    record = {
        "id": "",
        "theme": "answer_relevance",
        "question": "What is an ETF?",
        "expected_behavior": "Explain an ETF.",
        "required_terms": ["ETF"],
        "forbidden_terms": [],
        "source": "beta_user",
    }

    with pytest.raises(
        ValueError,
        match="'id' must be a non-empty string",
    ):
        service.validate_beta_case(record)


def test_validate_personalization_requirements():
    service = create_service()

    record = {
        "id": "BETA005",
        "theme": "personalization",
        "question": "Based on my profile, explain risk tolerance.",
        "expected_behavior": (
            "Use available user context without inventing "
            "missing profile information."
        ),
        "required_terms": ["risk", "tolerance"],
        "forbidden_terms": ["guaranteed"],
        "personalization_requirements": {
            "requires_available_context": True,
        },
        "source": "beta_user",
    }

    case = service.validate_beta_case(record)

    assert case.personalization_requirements == {
        "requires_available_context": True,
    }


def test_add_beta_cases_preserves_existing_cases():
    service = create_service()

    original = service.load_golden_set()
    original_count = len(original["cases"])

    record = {
        "id": "BETA006",
        "theme": "answer_relevance",
        "question": "What is an index fund?",
        "expected_behavior": (
            "Explain what an index fund is directly."
        ),
        "required_terms": ["index"],
        "forbidden_terms": ["guaranteed"],
        "source": "beta_user",
    }

    updated = service.add_beta_cases([record])

    assert len(updated["cases"]) == original_count + 1

    assert any(
        case["id"] == "BETA006"
        for case in updated["cases"]
    )

    assert len(original["cases"]) == original_count


def test_add_beta_cases_rejects_existing_case_id():
    service = create_service()

    existing_id = service.load_golden_set()["cases"][0]["id"]

    record = {
        "id": existing_id,
        "theme": "answer_relevance",
        "question": "Duplicate question.",
        "expected_behavior": "Explain clearly.",
        "required_terms": ["explain"],
        "forbidden_terms": [],
        "source": "beta_user",
    }

    with pytest.raises(
        ValueError,
        match="already exists in golden set",
    ):
        service.add_beta_cases([record])


def test_save_golden_set_creates_separate_file(tmp_path):
    service = create_service()

    record = {
        "id": "BETA007",
        "theme": "answer_relevance",
        "question": "What is a bond?",
        "expected_behavior": (
            "Explain what a bond is clearly."
        ),
        "required_terms": ["bond"],
        "forbidden_terms": ["guaranteed"],
        "source": "beta_user",
    }

    updated = service.add_beta_cases([record])

    output_path = tmp_path / "updated_golden_set.json"

    saved_path = service.save_golden_set(
        updated,
        str(output_path),
    )

    assert saved_path == output_path
    assert output_path.exists()

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        saved_data = json.load(file)

    assert any(
        case["id"] == "BETA007"
        for case in saved_data["cases"]
    )


def test_original_golden_set_is_not_modified(tmp_path):
    service = create_service()

    original = service.load_golden_set()
    original_ids = {
        case["id"]
        for case in original["cases"]
    }

    record = {
        "id": "BETA008",
        "theme": "topic_understanding",
        "question": "What is diversification?",
        "expected_behavior": (
            "Explain diversification clearly."
        ),
        "required_terms": ["diversification"],
        "forbidden_terms": [],
        "source": "beta_user",
    }

    updated = service.add_beta_cases([record])

    output_path = tmp_path / "updated_golden_set.json"

    service.save_golden_set(
        updated,
        str(output_path),
    )

    original_after = service.load_golden_set()

    original_ids_after = {
        case["id"]
        for case in original_after["cases"]
    }

    assert original_ids_after == original_ids
    assert "BETA008" not in original_ids_after