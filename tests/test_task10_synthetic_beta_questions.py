from app.services.feedback_dataset_service import (
    FeedbackDatasetService,
)


DATASET_PATH = "tests/data/task10_synthetic_beta_questions.json"


def create_service():
    return FeedbackDatasetService(DATASET_PATH)


def test_synthetic_beta_dataset_loads():
    service = create_service()

    records = service.load_records()

    assert len(records) == 30


def test_synthetic_beta_dataset_has_ten_themes():
    service = create_service()

    records = service.load_records()

    themes = {record.theme for record in records}

    assert themes == {
        "answer_relevance",
        "topic_understanding",
        "rag_relevance",
        "explanation_clarity",
        "response_conciseness",
        "personalization",
        "conversation_continuity",
        "insufficient_knowledge",
        "news_sentiment",
        "risk_factor_explainability",
    }


def test_each_theme_has_three_questions():
    service = create_service()

    records = service.load_records()

    counts = {}

    for record in records:
        counts[record.theme] = counts.get(record.theme, 0) + 1

    assert len(counts) == 10

    for theme, count in counts.items():
        assert count == 3


def test_all_records_are_synthetic_pre_deployment():
    service = create_service()

    records = service.load_records()

    assert len(records) == 30

    for record in records:
        assert record.source == "simulated_pre_deployment"


def test_record_ids_are_unique():
    service = create_service()

    records = service.load_records()

    record_ids = [record.record_id for record in records]

    assert len(record_ids) == len(set(record_ids))


def test_synthetic_dataset_contains_expected_id_range():
    service = create_service()

    records = service.load_records()

    record_ids = {record.record_id for record in records}

    expected_ids = {
        f"SYN{i:03d}"
        for i in range(1, 31)
    }

    assert record_ids == expected_ids


def test_get_records_by_theme_returns_three_records():
    service = create_service()

    records = service.get_records_by_theme(
        "personalization"
    )

    assert len(records) == 3

    for record in records:
        assert record.theme == "personalization"
        assert record.source == "simulated_pre_deployment"


def test_get_records_by_source_returns_all_synthetic_records():
    service = create_service()

    records = service.get_records_by_source(
        "simulated_pre_deployment"
    )

    assert len(records) == 30


def test_no_real_beta_records_are_present():
    service = create_service()

    beta_records = service.get_records_by_source(
        "beta_user"
    )

    assert beta_records == []