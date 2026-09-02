import os

import requests
from dotenv import load_dotenv


load_dotenv()

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")


def send_batch_error_message(errors):
    
    if not SLACK_WEBHOOK:
        print("Slack Webhook not available.")
        return

    failed_user_ids = [str(item["user_id"]) for item in errors]

    payload = {
        "text": (
            f"Portfolio Insight DAG completed with {len(errors)} error(s).\n"
            f"Failed user_ids: {', '.join(failed_user_ids)}"
        )
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