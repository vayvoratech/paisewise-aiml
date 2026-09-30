from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class ModelVersion:
    model_name: str
    version: str
    created_at: str
    metrics: dict[str, float]
    dataset_version: str


class ModelVersioning:
    """Creates version metadata for all Task 7 models."""

    @staticmethod
    def create_version(
        model_name: str,
        version: str,
        metrics: dict[str, float],
        dataset_version: str,
    ) -> ModelVersion:

        if not model_name or not model_name.strip():
            raise ValueError("model_name cannot be empty")

        if not version or not version.strip():
            raise ValueError("version cannot be empty")

        if not dataset_version or not dataset_version.strip():
            raise ValueError("dataset_version cannot be empty")

        if not isinstance(metrics, dict):
            raise TypeError("metrics must be a dictionary")

        return ModelVersion(
            model_name=model_name.strip(),
            version=version.strip(),
            created_at=datetime.now(timezone.utc).isoformat(),
            metrics={
                key: float(value)
                for key, value in metrics.items()
            },
            dataset_version=dataset_version.strip(),
        )