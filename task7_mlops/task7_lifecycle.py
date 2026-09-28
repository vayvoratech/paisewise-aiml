from dataclasses import dataclass

from task7_mlops.model_lifecycle import ModelLifecycle
from task7_mlops.shadow_monitor import ShadowMonitoringService
from task7_mlops.rollback import RollbackDecision
from task7_mlops.lifecycle_notification import (
    LifecycleNotificationService,
)


@dataclass
class Task7LifecycleResult:
    model_name: str
    model_version: str
    dataset_version: str
    rollback_decision: RollbackDecision


class Task7LifecycleService:
    """
    Main orchestration layer for Task 7.

    Handles:
    - model versioning
    - shadow execution
    - anomaly monitoring
    - automatic rollback
    - Slack notification

    Existing application files are not modified.
    """

    def __init__(
        self,
        rollback_threshold: float = 0.05,
    ) -> None:

        self.lifecycle = ModelLifecycle(
            rollback_threshold=rollback_threshold
        )

        self.shadow_monitor = ShadowMonitoringService(
            anomaly_threshold=rollback_threshold
        )

        self.notification = (
            LifecycleNotificationService()
        )

    def create_model_version(
        self,
        model_name: str,
        version: str,
        metrics: dict[str, float],
        dataset_version: str,
    ):
        return self.lifecycle.create_version(
            model_name=model_name,
            version=version,
            metrics=metrics,
            dataset_version=dataset_version,
        )

    def process_shadow_user(
        self,
        user_id: str,
        current_model,
        shadow_model,
        input_data,
        current_version: str,
        previous_version: str,
    ):
        return self.shadow_monitor.process_user(
            user_id=user_id,
            current_model=current_model,
            shadow_model=shadow_model,
            input_data=input_data,
            current_version=current_version,
            previous_version=previous_version,
        )

    def evaluate_rollback(
        self,
        model_name: str,
        current_version: str,
        previous_version: str,
        previous_metric: float = 0.0,
        new_metric: float = 0.0,
    ) -> RollbackDecision:

        decision = self.shadow_monitor.evaluate(
            current_version=current_version,
            previous_version=previous_version,
        )

        self.notification.notify_rollback(
            model_name=model_name,
            decision=decision,
            previous_version=previous_version,
            new_version=current_version,
            previous_metric=previous_metric,
            new_metric=new_metric,
        )

        return decision

    def reset_monitor(self) -> None:
        self.shadow_monitor.reset()