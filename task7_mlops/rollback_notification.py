from task7_mlops.rollback import RollbackDecision
from task7_mlops.slack_notification import SlackRetrainingNotifier


class RollbackNotificationService:
    """
    Sends a Slack notification when automatic rollback is triggered.
    """

    def __init__(self) -> None:
        self.notifier = SlackRetrainingNotifier()

    def handle(
        self,
        decision: RollbackDecision,
        model_name: str,
        previous_version: str,
        new_version: str,
        previous_metric: float,
        new_metric: float,
    ) -> bool:
        """
        Notify Slack when rollback is required.

        Returns True when a notification was sent.
        """

        if not decision.rollback_required:
            return False

        self.notifier.notify(
            model_name=model_name,
            previous_version=previous_version,
            new_version=new_version,
            previous_metric=previous_metric,
            new_metric=new_metric,
        )

        return True