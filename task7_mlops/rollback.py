from dataclasses import dataclass


@dataclass
class RollbackDecision:
    anomaly_rate: float
    threshold: float
    rollback_required: bool
    active_version: str


class AutomaticRollback:
    """Determines whether the previous model version must be restored."""

    def __init__(self, threshold: float = 0.05):
        if not 0 < threshold < 1:
            raise ValueError(
                "threshold must be between 0 and 1"
            )

        self.threshold = threshold

    def evaluate(
        self,
        total_users: int,
        anomalous_users: int,
        current_version: str,
        previous_version: str,
    ) -> RollbackDecision:

        if total_users <= 0:
            raise ValueError(
                "total_users must be greater than 0"
            )

        if anomalous_users < 0:
            raise ValueError(
                "anomalous_users cannot be negative"
            )

        if anomalous_users > total_users:
            raise ValueError(
                "anomalous_users cannot exceed total_users"
            )

        anomaly_rate = anomalous_users / total_users

        rollback_required = (
            anomaly_rate > self.threshold
        )

        active_version = (
            previous_version
            if rollback_required
            else current_version
        )

        return RollbackDecision(
            anomaly_rate=anomaly_rate,
            threshold=self.threshold,
            rollback_required=rollback_required,
            active_version=active_version,
        )