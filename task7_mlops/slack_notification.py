import os
import requests


class SlackRetrainingNotifier:
    """Sends model retraining notifications to Slack."""

    def __init__(self, webhook_env: str = "SLACK_URL"):
        self.webhook_url = os.getenv(webhook_env)

        if not self.webhook_url:
            raise RuntimeError(
                f"{webhook_env} is not configured"
            )

    def notify(
        self,
        model_name: str,
        previous_version: str,
        new_version: str,
        previous_metric: float,
        new_metric: float,
    ) -> None:

        metric_change = new_metric - previous_metric

        message = {
            "text": (
                "🤖 Model Retraining Completed\n\n"
                f"Model: {model_name}\n"
                f"Previous version: {previous_version}\n"
                f"New version: {new_version}\n"
                f"Previous metric: {previous_metric:.4f}\n"
                f"New metric: {new_metric:.4f}\n"
                f"Metric change: {metric_change:+.4f}"
            )
        }

        response = requests.post(
            self.webhook_url,
            json=message,
            timeout=10,
        )

        response.raise_for_status()

        print(
            f"Slack notification sent for {model_name}"
        )