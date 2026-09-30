from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.schemas.mlops import ModelVersionMetadata
from app.services.mlops.mlflow_registry_service import (
    MLflowRegistryService,
)


def create_metadata() -> ModelVersionMetadata:
    return ModelVersionMetadata(
        model_name="test-model",
        version="v1",
        created_at=datetime.now(timezone.utc),
        metrics={
            "accuracy": 0.95,
            "f1_score": 0.93,
        },
        dataset_version="dataset-v1",
    )


def test_service_uses_default_tracking_uri():
    service = MLflowRegistryService()

    assert service.tracking_uri


@patch(
    "app.services.mlops.mlflow_registry_service.mlflow.start_run"
)
@patch(
    "app.services.mlops.mlflow_registry_service.mlflow.set_tag"
)
@patch(
    "app.services.mlops.mlflow_registry_service.mlflow.log_metrics"
)
def test_start_run_logs_metadata_and_metrics(
    mock_log_metrics,
    mock_set_tag,
    mock_start_run,
):
    mock_start_run.return_value = "test-run"

    service = MLflowRegistryService()
    metadata = create_metadata()

    result = service.start_run(metadata)

    assert result == "test-run"

    assert mock_set_tag.call_count == 4

    mock_log_metrics.assert_called_once_with(
        metadata.metrics
    )


@patch(
    "app.services.mlops.mlflow_registry_service.mlflow.active_run"
)
@patch(
    "app.services.mlops.mlflow_registry_service.mlflow.end_run"
)
def test_end_run_ends_active_run(
    mock_end_run,
    mock_active_run,
):
    mock_active_run.return_value = "active-run"

    MLflowRegistryService.end_run()

    mock_end_run.assert_called_once()


@patch(
    "app.services.mlops.mlflow_registry_service.mlflow.active_run"
)
@patch(
    "app.services.mlops.mlflow_registry_service.mlflow.end_run"
)
def test_end_run_does_nothing_without_active_run(
    mock_end_run,
    mock_active_run,
):
    mock_active_run.return_value = None

    MLflowRegistryService.end_run()

    mock_end_run.assert_not_called()


@patch(
    "app.services.mlops.mlflow_registry_service.mlflow.register_model"
)
def test_register_model_calls_mlflow(
    mock_register_model,
):
    mock_register_model.return_value = "registered-model"

    result = MLflowRegistryService.register_model(
        model_uri="runs:/abc123/model",
        model_name="test-model",
    )

    assert result == "registered-model"

    mock_register_model.assert_called_once_with(
        model_uri="runs:/abc123/model",
        name="test-model",
    )


@pytest.mark.parametrize(
    "model_uri,model_name",
    [
        ("", "test-model"),
        ("runs:/abc123/model", ""),
    ],
)
def test_register_model_rejects_empty_values(
    model_uri,
    model_name,
):
    with pytest.raises(ValueError):
        MLflowRegistryService.register_model(
            model_uri=model_uri,
            model_name=model_name,
        )