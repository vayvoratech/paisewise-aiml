from task7_mlops.rollback import RollbackDecision
from task7_mlops.slack_notification import SlackRetrainingNotifier


class LifecycleNotificationService:
    """
    Connects automatic rollback decisions to Slack notifications.

    Existing application files are not modified.
    """

    def __init__(self) -> None:
        self.notifier = SlackRetrainingNotifier()

    def notify_rollback(
        self,
        model_name: str,
        decision: RollbackDecision,
        previous_version: str,
        new_version: str,
        previous_metric: float,
        new_metric: float,
    ) -> bool:
        """
        Send a Slack notification only when rollback is triggered.
        """

        if not decision.rollback_required:
            print(
                f"No rollback required for {model_name}. "
                f"Anomaly rate: {decision.anomaly_rate:.2%}"
            )
            return False

        self.notifier.notify(
            model_name=model_name,
            previous_version=previous_version,
            new_version=new_version,
            previous_metric=previous_metric,
            new_metric=new_metric,
        )

        print(
            f"Rollback triggered for {model_name}: "
            f"{new_version} -> {decision.active_version}"
        )

        return True