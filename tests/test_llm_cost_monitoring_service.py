from datetime import date

from app.services.llm_cost_monitoring_service import (
    LLMCostMonitoringService,
)


class FakeCostService:
    def __init__(self, daily_cost: float, daily_budget: float) -> None:
        self.daily_cost = daily_cost
        self.daily_budget = daily_budget

    def get_daily_cost(self, target_date=None) -> float:
        return self.daily_cost


class FakeSlackService:
    def __init__(self) -> None:
        self.messages = []

    def notify(self, message: str) -> None:
        self.messages.append(message)


def test_budget_exceeded_sends_slack_alert():
    cost_service = FakeCostService(
        daily_cost=0.0015,
        daily_budget=0.001,
    )
    slack_service = FakeSlackService()

    monitoring_service = LLMCostMonitoringService(
        cost_service=cost_service,
        slack_service=slack_service,
    )

    result = monitoring_service.check_daily_budget(
        date(2026, 9, 16)
    )

    assert result is True
    assert len(slack_service.messages) == 1
    assert "LLM Daily Budget Exceeded" in slack_service.messages[0]
    assert "$0.001500" in slack_service.messages[0]
    assert "$0.001000" in slack_service.messages[0]


def test_budget_within_limit_does_not_send_alert():
    cost_service = FakeCostService(
        daily_cost=0.0005,
        daily_budget=0.001,
    )
    slack_service = FakeSlackService()

    monitoring_service = LLMCostMonitoringService(
        cost_service=cost_service,
        slack_service=slack_service,
    )

    result = monitoring_service.check_daily_budget(
        date(2026, 9, 16)
    )

    assert result is False
    assert len(slack_service.messages) == 0


def test_zero_budget_disables_monitoring():
    cost_service = FakeCostService(
        daily_cost=0.0100,
        daily_budget=0.0,
    )
    slack_service = FakeSlackService()

    monitoring_service = LLMCostMonitoringService(
        cost_service=cost_service,
        slack_service=slack_service,
    )

    result = monitoring_service.check_daily_budget(
        date(2026, 9, 16)
    )

    assert result is False
    assert len(slack_service.messages) == 0