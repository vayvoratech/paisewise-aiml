from dataclasses import dataclass

from task7_mlops.model_versioning import (
    ModelVersion,
    ModelVersioning,
)
from task7_mlops.rollback import (
    AutomaticRollback,
    RollbackDecision,
)


@dataclass
class ModelLifecycleResult:
    model_version: ModelVersion
    rollback: RollbackDecision


class ModelLifecycle:
    """Coordinates Task 7 lifecycle operations for a model."""

    def __init__(self, rollback_threshold: float = 0.05):
        self.versioning = ModelVersioning()
        self.rollback = AutomaticRollback(
            threshold=rollback_threshold
        )

    def create_version(
        self,
        model_name: str,
        version: str,
        metrics: dict[str, float],
        dataset_version: str,
    ) -> ModelVersion:

        return self.versioning.create_version(
            model_name=model_name,
            version=version,
            metrics=metrics,
            dataset_version=dataset_version,
        )

    def evaluate_rollback(
        self,
        total_users: int,
        anomalous_users: int,
        current_version: str,
        previous_version: str,
    ) -> RollbackDecision:

        return self.rollback.evaluate(
            total_users=total_users,
            anomalous_users=anomalous_users,
            current_version=current_version,
            previous_version=previous_version,
        )

    def process_model(
        self,
        model_name: str,
        version: str,
        metrics: dict[str, float],
        dataset_version: str,
        total_users: int,
        anomalous_users: int,
        previous_version: str,
    ) -> ModelLifecycleResult:

        model_version = self.create_version(
            model_name=model_name,
            version=version,
            metrics=metrics,
            dataset_version=dataset_version,
        )

        rollback = self.evaluate_rollback(
            total_users=total_users,
            anomalous_users=anomalous_users,
            current_version=version,
            previous_version=previous_version,
        )

        return ModelLifecycleResult(
            model_version=model_version,
            rollback=rollback,
        )