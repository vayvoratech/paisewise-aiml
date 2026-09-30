import os
import requests

previous_version = "v1"
new_version = "v2"

previous_metric = 0.82
new_metric = 0.87

improvement = new_metric - previous_metric

webhook_url = os.getenv("SLACK_URL")

if not webhook_url:
    raise RuntimeError("SLACK_URL is not configured")

message = {
    "text": (
        "🤖 Model Retraining Completed\n\n"
        f"Model version: {new_version}\n"
        f"Previous version: {previous_version}\n"
        f"Previous metric: {previous_metric:.2f}\n"
        f"New metric: {new_metric:.2f}\n"
        f"Metric change: {improvement:+.2f}"
    )
}

response = requests.post(
    webhook_url,
    json=message,
    timeout=10,
)

response.raise_for_status()

print("✅ Slack notification sent successfully")