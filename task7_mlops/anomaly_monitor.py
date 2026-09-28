from dataclasses import dataclass

from task7_mlops.rollback import AutomaticRollback, RollbackDecision


@dataclass
class AnomalyMonitorResult:
    total_users: int
    anomalous_users: int
    anomaly_rate: float
    rollback_decision: RollbackDecision


class AnomalyMonitor:
    """
    Tracks shadow anomalies across users and evaluates
    the Task 7 automatic rollback threshold.

    Existing application files are not modified.
    """

    def __init__(
        self,
        threshold: float = 0.05,
    ) -> None:
        self.rollback = AutomaticRollback(
            threshold=threshold
        )
        self.total_users = 0
        self.anomalous_users = 0

    def record(
        self,
        is_anomaly: bool,
    ) -> None:
        self.total_users += 1

        if is_anomaly:
            self.anomalous_users += 1

    def evaluate(
        self,
        current_version: str,
        previous_version: str,
    ) -> AnomalyMonitorResult:

        if self.total_users == 0:
            raise ValueError(
                "No users have been recorded"
            )

        anomaly_rate = (
            self.anomalous_users
            / self.total_users
        )

        decision = self.rollback.evaluate(
            total_users=self.total_users,
            anomalous_users=self.anomalous_users,
            current_version=current_version,
            previous_version=previous_version,
        )

        return AnomalyMonitorResult(
            total_users=self.total_users,
            anomalous_users=self.anomalous_users,
            anomaly_rate=anomaly_rate,
            rollback_decision=decision,
        )

    def reset(self) -> None:
        self.total_users = 0
        self.anomalous_users = 0