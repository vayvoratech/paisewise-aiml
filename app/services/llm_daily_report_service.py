from datetime import date

from app.services.llm_cost_service import LLMCostService
from app.services.llm_usage_repository import LLMUsageRepository


class LLMDailyReportService:
    """Builds the daily LLM cost and performance report."""

    def __init__(
        self,
        usage_repository: LLMUsageRepository,
        cost_service: LLMCostService,
    ) -> None:
        self.usage_repository = usage_repository
        self.cost_service = cost_service

    def generate_report(self, target_date: date | None = None) -> str:
        """Generate a Slack-ready daily LLM cost and performance report."""

        if target_date is None:
            target_date = date.today()

        summary = self.usage_repository.get_daily_usage_summary(target_date)

        daily_budget = self.cost_service.daily_budget
        total_cost = summary["total_cost"]

        if daily_budget > 0:
            budget_utilization = (total_cost / daily_budget) * 100
            budget_status = (
                "Exceeded"
                if total_cost > daily_budget
                else "Within Budget"
            )
        else:
            budget_utilization = 0.0
            budget_status = "Budget Not Configured"

        average_latency = summary["average_latency_ms"]

        if average_latency is None:
            latency_text = "N/A"
        else:
            latency_text = f"{average_latency:.2f} ms"

        return (
            "📊 AI Service Daily Cost & Performance Report\n\n"
            f"Date: {target_date}\n\n"
            "Usage\n"
            f"Requests:          {summary['request_count']}\n"
            f"Input Tokens:      {summary['input_tokens']}\n"
            f"Output Tokens:     {summary['output_tokens']}\n"
            f"Total Tokens:      {summary['total_tokens']}\n"
            f"Models Used:       {summary['model_count']}\n\n"
            "Cost\n"
            f"Total Cost:        ${total_cost:.6f}\n"
            f"Daily Budget:      ${daily_budget:.6f}\n"
            f"Budget Used:       {budget_utilization:.2f}%\n"
            f"Budget Status:     {budget_status}\n\n"
            "Performance\n"
            f"Average Latency:   {latency_text}"
        )