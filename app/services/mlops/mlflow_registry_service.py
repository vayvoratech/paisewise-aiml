from typing import Any

import mlflow

from app.schemas.mlops import ModelVersionMetadata


class MLflowRegistryService:
    """Handles MLflow tracking and model registration."""

    def __init__(
        self,
        tracking_uri: str | None = None,
    ) -> None:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)

        self.tracking_uri = mlflow.get_tracking_uri()

    def start_run(
        self,
        metadata: ModelVersionMetadata,
    ) -> Any:
        run = mlflow.start_run()

        mlflow.set_tag(
            "model_name",
            metadata.model_name,
        )

        mlflow.set_tag(
            "model_version",
            metadata.version,
        )

        mlflow.set_tag(
            "dataset_version",
            metadata.dataset_version,
        )

        mlflow.set_tag(
            "created_at",
            metadata.created_at.isoformat(),
        )

        mlflow.log_metrics(metadata.metrics)

        return run

    @staticmethod
    def end_run() -> None:
        if mlflow.active_run() is not None:
            mlflow.end_run()

    @staticmethod
    def register_model(
        model_uri: str,
        model_name: str,
    ) -> Any:
        if not model_uri or not model_uri.strip():
            raise ValueError("model_uri cannot be empty")

        if not model_name or not model_name.strip():
            raise ValueError("model_name cannot be empty")

        return mlflow.register_model(
            model_uri=model_uri,
            name=model_name.strip(),
        )