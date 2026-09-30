import json

import pytest

from app.services.feedback_dataset_service import (
    FeedbackDatasetService,
)


def write_dataset(tmp_path, data):
    dataset_path = tmp_path / "feedback_dataset.json"

    with dataset_path.open("w", encoding="utf-8") as file:
        json.dump(data, file)

    return dataset_path


def valid_record(
    record_id="FB001",
    case_id="TC001",
    theme="answer_relevance",
    feedback="down",
    category="answer_relevance",
    comment="The response should answer the question more directly.",
    source="simulated_pre_deployment",
):
    return {
        "id": record_id,
        "case_id": case_id,
        "theme": theme,
        "feedback": feedback,
        "category": category,
        "comment": comment,
        "source": source,
    }


def test_load_valid_dataset(tmp_path):
    data = {
        "dataset_name": "task10_simulated_feedback",
        "version": "1.0",
        "status": "pre_deployment",
        "source": "simulated_pre_deployment",
        "records": [
            valid_record(),
        ],
    }

    dataset_path = write_dataset(tmp_path, data)

    service = FeedbackDatasetService(dataset_path)

    records = service.load_records()

    assert len(records) == 1
    assert records[0].record_id == "FB001"
    assert records[0].case_id == "TC001"
    assert records[0].theme == "answer_relevance"
    assert records[0].feedback == "down"
    assert records[0].source == "simulated_pre_deployment"


def test_get_records_by_theme(tmp_path):
    data = {
        "records": [
            valid_record(
                record_id="FB001",
                theme="answer_relevance",
            ),
            valid_record(
                record_id="FB002",
                case_id="TC002",
                theme="topic_understanding",
                category="topic_understanding",
            ),
        ],
    }

    dataset_path = write_dataset(tmp_path, data)

    service = FeedbackDatasetService(dataset_path)

    records = service.get_records_by_theme("answer_relevance")

    assert len(records) == 1
    assert records[0].record_id == "FB001"


def test_get_records_by_source(tmp_path):
    data = {
        "records": [
            valid_record(
                record_id="FB001",
                source="simulated_pre_deployment",
            ),
            valid_record(
                record_id="FB002",
                source="beta_user",
            ),
        ],
    }

    dataset_path = write_dataset(tmp_path, data)

    service = FeedbackDatasetService(dataset_path)

    simulated_records = service.get_records_by_source(
        "simulated_pre_deployment"
    )

    beta_records = service.get_records_by_source("beta_user")

    assert len(simulated_records) == 1
    assert simulated_records[0].record_id == "FB001"

    assert len(beta_records) == 1
    assert beta_records[0].record_id == "FB002"


def test_invalid_feedback_is_rejected(tmp_path):
    data = {
        "records": [
            valid_record(
                feedback="invalid",
            ),
        ],
    }

    dataset_path = write_dataset(tmp_path, data)

    service = FeedbackDatasetService(dataset_path)

    with pytest.raises(ValueError, match="Invalid feedback"):
        service.load_records()


def test_invalid_source_is_rejected(tmp_path):
    data = {
        "records": [
            valid_record(
                source="unknown_source",
            ),
        ],
    }

    dataset_path = write_dataset(tmp_path, data)

    service = FeedbackDatasetService(dataset_path)

    with pytest.raises(ValueError, match="Invalid source"):
        service.load_records()


def test_duplicate_record_ids_are_rejected(tmp_path):
    data = {
        "records": [
            valid_record(record_id="FB001"),
            valid_record(
                record_id="FB001",
                case_id="TC002",
                theme="topic_understanding",
                category="topic_understanding",
            ),
        ],
    }

    dataset_path = write_dataset(tmp_path, data)

    service = FeedbackDatasetService(dataset_path)

    with pytest.raises(ValueError, match="Duplicate feedback record ID"):
        service.load_records()


def test_records_must_be_a_list(tmp_path):
    data = {
        "records": {},
    }

    dataset_path = write_dataset(tmp_path, data)

    service = FeedbackDatasetService(dataset_path)

    with pytest.raises(ValueError, match="'records' must be a list"):
        service.load_records()


def test_missing_required_field_is_rejected(tmp_path):
    record = valid_record()
    del record["case_id"]

    data = {
        "records": [record],
    }

    dataset_path = write_dataset(tmp_path, data)

    service = FeedbackDatasetService(dataset_path)

    with pytest.raises(ValueError, match="'case_id' must be a string"):
        service.load_records()


def test_missing_dataset_is_rejected(tmp_path):
    dataset_path = tmp_path / "does_not_exist.json"

    service = FeedbackDatasetService(dataset_path)

    with pytest.raises(FileNotFoundError, match="Feedback dataset not found"):
        service.load_records()


def test_invalid_json_is_rejected(tmp_path):
    dataset_path = tmp_path / "invalid.json"
    dataset_path.write_text(
        '{"records": [invalid json]}',
        encoding="utf-8",
    )

    service = FeedbackDatasetService(dataset_path)

    with pytest.raises(ValueError, match="Invalid JSON feedback dataset"):
        service.load_records()