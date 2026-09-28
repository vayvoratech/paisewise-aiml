import pytest

from app.services.slack_notification_service import SlackNotificationService


def test_missing_webhook_configuration(monkeypatch):
    monkeypatch.delenv("SLACK_URL", raising=False)

    with pytest.raises(RuntimeError, match="SLACK_URL is not configured"):
        SlackNotificationService()


def test_empty_message_rejected(monkeypatch):
    monkeypatch.setenv("SLACK_URL", "https://example.com/webhook")

    service = SlackNotificationService()

    with pytest.raises(ValueError, match="message cannot be empty"):
        service.notify("")


def test_notification_sent(monkeypatch):
    monkeypatch.setenv("SLACK_URL", "https://example.com/webhook")

    captured = {}

    class MockResponse:
        def raise_for_status(self):
            pass

    def mock_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return MockResponse()

    monkeypatch.setattr(
        "app.services.slack_notification_service.requests.post",
        mock_post,
    )

    service = SlackNotificationService()
    service.notify("Test Slack notification")

    assert captured["url"] == "https://example.com/webhook"
    assert captured["json"] == {"text": "Test Slack notification"}
    assert captured["timeout"] == 10