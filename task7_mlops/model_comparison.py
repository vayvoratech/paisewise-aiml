from dataclasses import dataclass


@dataclass
class ModelComparisonResult:
    model_name: str
    previous_version: str
    new_version: str
    previous_metric: float
    new_metric: float
    metric_change: float
    improved: bool


class ModelComparison:
    """
    Compares the evaluation metric of two model versions.
    """

    @staticmethod
    def compare(
        model_name: str,
        previous_version: str,
        new_version: str,
        previous_metric: float,
        new_metric: float,
    ) -> ModelComparisonResult:

        if not model_name or not model_name.strip():
            raise ValueError("model_name cannot be empty")

        if not previous_version or not previous_version.strip():
            raise ValueError(
                "previous_version cannot be empty"
            )

        if not new_version or not new_version.strip():
            raise ValueError(
                "new_version cannot be empty"
            )

        metric_change = (
            float(new_metric) - float(previous_metric)
        )

        return ModelComparisonResult(
            model_name=model_name.strip(),
            previous_version=previous_version.strip(),
            new_version=new_version.strip(),
            previous_metric=float(previous_metric),
            new_metric=float(new_metric),
            metric_change=metric_change,
            improved=metric_change > 0,
        )