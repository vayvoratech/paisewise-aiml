from dataclasses import dataclass
from typing import Any, Callable

from task7_mlops.anomaly_monitor import AnomalyMonitor
from task7_mlops.rollback import RollbackDecision
from task7_mlops.shadow_deployment import ShadowDeployment


@dataclass
class ShadowMonitoringResult:
    user_id: str
    current_output: Any
    shadow_output: Any
    anomaly: bool
    rollback_decision: RollbackDecision | None


class ShadowMonitoringService:
    """
    Orchestrates shadow execution, anomaly tracking,
    and automatic rollback evaluation.

    Existing application files are not modified.
    """

    def __init__(
        self,
        anomaly_threshold: float = 0.05,
    ) -> None:
        self.monitor = AnomalyMonitor(
            threshold=anomaly_threshold
        )

    def process_user(
        self,
        user_id: str,
        current_model: Callable[[Any], Any],
        shadow_model: Callable[[Any], Any],
        input_data: Any,
        current_version: str,
        previous_version: str,
    ) -> ShadowMonitoringResult:

        if not user_id or not user_id.strip():
            raise ValueError(
                "user_id cannot be empty"
            )

        comparison = ShadowDeployment.run(
            current_model=current_model,
            shadow_model=shadow_model,
            input_data=input_data,
        )

        anomaly = not comparison.outputs_match

        self.monitor.record(anomaly)

        return ShadowMonitoringResult(
            user_id=user_id.strip(),
            current_output=comparison.current_output,
            shadow_output=comparison.shadow_output,
            anomaly=anomaly,
            rollback_decision=None,
        )

    def evaluate(
        self,
        current_version: str,
        previous_version: str,
    ) -> RollbackDecision:

        result = self.monitor.evaluate(
            current_version=current_version,
            previous_version=previous_version,
        )

        return result.rollback_decision

    def reset(self) -> None:
        self.monitor.reset()