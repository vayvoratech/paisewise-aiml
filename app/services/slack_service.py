import os

import requests
from dotenv import load_dotenv


load_dotenv()

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")


def send_success_message():
    if not SLACK_WEBHOOK:
        print("Slack Webhook not available.")
        return

    payload = {
        "text": "Portfolio Insight DAG completed successfully."
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK,
            json=payload,
            timeout=10,
        )

        print("Slack status:", response.status_code)
        print("Slack response:", response.text)

    except Exception as error:
        print("Slack notification error:", error)


def send_failure_message(error):
    if not SLACK_WEBHOOK:
        print("Slack Webhook not available.")
        return

    payload = {
        "text": f"Portfolio Insight DAG Failed.\nReason: {error}"
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK,
            json=payload,
            timeout=10,
        )

        print("Slack status:", response.status_code)
        print("Slack response:", response.text)

    except Exception as error:
        print("Slack notification error:", error)