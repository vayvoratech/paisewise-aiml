from dataclasses import dataclass
from typing import Dict


@dataclass
class ModelMetrics:
    model_name: str
    version: str
    metrics: Dict[str, float]


class MetricsTracker:
    @staticmethod
    def create_metrics(
        model_name: str,
        version: str,
        metrics: Dict[str, float],
    ) -> ModelMetrics:

        if not model_name:
            raise ValueError("model_name cannot be empty")

        if not version:
            raise ValueError("version cannot be empty")

        if not isinstance(metrics, dict):
            raise TypeError("metrics must be a dictionary")

        converted_metrics = {}

        for name, value in metrics.items():
            if not isinstance(name, str) or not name:
                raise ValueError("metric name must be a non-empty string")

            converted_metrics[name] = float(value)

        return ModelMetrics(
            model_name=model_name,
            version=version,
            metrics=converted_metrics,
        )

    @staticmethod
    def compare(
        previous: ModelMetrics,
        current: ModelMetrics,
    ) -> Dict[str, float]:

        if previous.model_name != current.model_name:
            raise ValueError("Cannot compare different models")

        changes = {}

        common_metrics = set(previous.metrics) & set(current.metrics)

        for metric in common_metrics:
            changes[metric] = (
                current.metrics[metric] - previous.metrics[metric]
            )

        return changes