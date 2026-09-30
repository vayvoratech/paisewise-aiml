from datetime import datetime, timezone

from app.schemas.mlops import ModelVersionMetadata


class ModelVersionService:
    """Creates metadata for versioned AI models."""

    @staticmethod
    def create_version(
        model_name: str,
        version: str,
        metrics: dict[str, float],
        dataset_version: str,
    ) -> ModelVersionMetadata:
        if not model_name or not model_name.strip():
            raise ValueError("model_name cannot be empty")

        if not version or not version.strip():
            raise ValueError("version cannot be empty")

        if not dataset_version or not dataset_version.strip():
            raise ValueError("dataset_version cannot be empty")

        if not isinstance(metrics, dict):
            raise TypeError("metrics must be a dictionary")

        if any(
            not isinstance(key, str) or not key.strip()
            for key in metrics
        ):
            raise ValueError("metric names cannot be empty")

        if any(
            not isinstance(value, (int, float))
            for value in metrics.values()
        ):
            raise TypeError("metric values must be numeric")

        return ModelVersionMetadata(
            model_name=model_name.strip(),
            version=version.strip(),
            created_at=datetime.now(timezone.utc),
            metrics={
                key.strip(): float(value)
                for key, value in metrics.items()
            },
            dataset_version=dataset_version.strip(),
        )