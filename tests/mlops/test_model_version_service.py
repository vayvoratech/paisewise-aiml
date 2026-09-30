from datetime import datetime

import pytest

from app.services.mlops.model_version_service import ModelVersionService


def test_create_version_generates_metadata():
    result = ModelVersionService.create_version(
        model_name="test-model",
        version="v1",
        metrics={
            "accuracy": 0.95,
            "f1_score": 0.93,
        },
        dataset_version="dataset-v1",
    )

    assert result.model_name == "test-model"
    assert result.version == "v1"
    assert result.metrics["accuracy"] == 0.95
    assert result.metrics["f1_score"] == 0.93
    assert result.dataset_version == "dataset-v1"
    assert isinstance(result.created_at, datetime)


@pytest.mark.parametrize(
    "model_name,version,dataset_version",
    [
        ("", "v1", "dataset-v1"),
        ("test-model", "", "dataset-v1"),
        ("test-model", "v1", ""),
    ],
)
def test_create_version_rejects_empty_required_values(
    model_name,
    version,
    dataset_version,
):
    with pytest.raises(ValueError):
        ModelVersionService.create_version(
            model_name=model_name,
            version=version,
            metrics={"accuracy": 0.95},
            dataset_version=dataset_version,
        )


def test_create_version_rejects_non_dictionary_metrics():
    with pytest.raises(TypeError):
        ModelVersionService.create_version(
            model_name="test-model",
            version="v1",
            metrics=[],  # type: ignore[arg-type]
            dataset_version="dataset-v1",
        )


def test_create_version_rejects_non_numeric_metrics():
    with pytest.raises(TypeError):
        ModelVersionService.create_version(
            model_name="test-model",
            version="v1",
            metrics={"accuracy": "high"},  # type: ignore[dict-item]
            dataset_version="dataset-v1",
        )


def test_create_version_strips_text_values():
    result = ModelVersionService.create_version(
        model_name="  test-model  ",
        version="  v1  ",
        metrics={" accuracy ": 0.95},
        dataset_version="  dataset-v1  ",
    )

    assert result.model_name == "test-model"
    assert result.version == "v1"
    assert result.dataset_version == "dataset-v1"
    assert result.metrics["accuracy"] == 0.95