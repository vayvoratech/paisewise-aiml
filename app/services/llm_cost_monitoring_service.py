from datetime import date

from app.services.llm_cost_service import LLMCostService
from app.services.slack_notification_service import SlackNotificationService


class LLMCostMonitoringService:
    """Monitors daily LLM spend and sends Slack alerts when the budget is exceeded."""

    def __init__(
        self,
        cost_service: LLMCostService,
        slack_service: SlackNotificationService,
    ) -> None:
        self.cost_service = cost_service
        self.slack_service = slack_service

    def check_daily_budget(
        self,
        target_date: date | None = None,
    ) -> bool:
        """Check daily LLM spend and alert Slack when the budget is exceeded."""

        if self.cost_service.daily_budget <= 0:
            return False

        daily_cost = self.cost_service.get_daily_cost(target_date)

        if daily_cost <= self.cost_service.daily_budget:
            return False

        message = (
            "🚨 LLM Daily Budget Exceeded\n\n"
            f"Date: {target_date or 'today'}\n"
            f"Daily Cost: ${daily_cost:.6f}\n"
            f"Configured Budget: ${self.cost_service.daily_budget:.6f}"
        )

        self.slack_service.notify(message)

        return True