from app.services.llm_cost_service import LLMCostService
from app.services.llm_daily_report_scheduler import LLMDailyReportScheduler
from app.services.llm_daily_report_service import LLMDailyReportService
from app.services.llm_usage_repository import LLMUsageRepository


def create_scheduler() -> LLMDailyReportScheduler:
    """Create the configured daily LLM report scheduler."""

    usage_repository = LLMUsageRepository()

    cost_service = LLMCostService.from_environment(
        usage_repository=usage_repository
    )

    report_service = LLMDailyReportService(
        usage_repository=usage_repository,
        cost_service=cost_service,
    )

    return LLMDailyReportScheduler(
        report_service=report_service,
    )


def main() -> None:
    """Start the daily LLM report scheduler."""

    scheduler = create_scheduler()

    try:
        scheduler.start()

        # Keep this process alive while the background scheduler runs.
        import time

        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        scheduler.shutdown()


if __name__ == "__main__":
    main()