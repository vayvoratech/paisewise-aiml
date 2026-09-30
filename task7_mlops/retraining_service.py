from task7_mlops.model_comparison import ModelComparison
from task7_mlops.slack_notification import SlackRetrainingNotifier


class RetrainingService:
    def __init__(self):
        self.notifier = SlackRetrainingNotifier()

    def evaluate_retraining(
        self,
        model_name: str,
        previous_version: str,
        new_version: str,
        previous_metric: float,
        new_metric: float,
    ):
        comparison = ModelComparison.compare(
            model_name=model_name,
            previous_version=previous_version,
            new_version=new_version,
            previous_metric=previous_metric,
            new_metric=new_metric,
        )

        self.notifier.notify(
            model_name=model_name,
            previous_version=previous_version,
            new_version=new_version,
            previous_metric=previous_metric,
            new_metric=new_metric,
        )

        return comparison