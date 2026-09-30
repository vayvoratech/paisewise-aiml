import os

import requests


class SlackNotificationService:
    """Sends notifications to Slack using an incoming webhook."""

    def __init__(self, webhook_env: str = "SLACK_URL") -> None:
        self.webhook_url = os.getenv(webhook_env)

        if not self.webhook_url:
            raise RuntimeError(f"{webhook_env} is not configured")

    def notify(self, message: str) -> None:
        """Send a text message to Slack."""
        if not message or not message.strip():
            raise ValueError("message cannot be empty")

        response = requests.post(
            self.webhook_url,
            json={"text": message.strip()},
            timeout=10,
        )

        response.raise_for_status()