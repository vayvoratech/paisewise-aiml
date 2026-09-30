from unittest.mock import Mock, patch

from app.services.llm_daily_report_scheduler import LLMDailyReportScheduler


def test_send_daily_report_generates_and_sends_report():
    report_service = Mock()
    report_service.generate_report.return_value = "Daily AI report"

    scheduler = LLMDailyReportScheduler(
        report_service=report_service,
        hour=9,
        minute=0,
    )

    with patch(
        "app.services.llm_daily_report_scheduler.SlackNotificationService"
    ) as slack_class:
        slack_service = slack_class.return_value

        scheduler.send_daily_report()

        report_service.generate_report.assert_called_once_with()
        slack_service.notify.assert_called_once_with("Daily AI report")


def test_scheduler_registers_daily_job():
    report_service = Mock()

    scheduler = LLMDailyReportScheduler(
        report_service=report_service,
        hour=9,
        minute=0,
    )

    with patch.object(scheduler.scheduler, "add_job") as add_job:
        with patch.object(scheduler.scheduler, "start"):

            scheduler.start()

            add_job.assert_called_once()

            kwargs = add_job.call_args.kwargs

            assert kwargs["trigger"] == "cron"
            assert kwargs["hour"] == 9
            assert kwargs["minute"] == 0
            assert kwargs["id"] == "llm_daily_report"
            assert kwargs["replace_existing"] is True


def test_scheduler_rejects_invalid_hour():
    report_service = Mock()

    try:
        LLMDailyReportScheduler(
            report_service=report_service,
            hour=24,
            minute=0,
        )
        assert False
    except ValueError:
        assert True


def test_scheduler_rejects_invalid_minute():
    report_service = Mock()

    try:
        LLMDailyReportScheduler(
            report_service=report_service,
            hour=9,
            minute=60,
        )
        assert False
    except ValueError:
        assert True


def test_scheduler_reads_schedule_from_environment(monkeypatch):
    report_service = Mock()

    monkeypatch.setenv("LLM_DAILY_REPORT_HOUR", "18")
    monkeypatch.setenv("LLM_DAILY_REPORT_MINUTE", "30")

    scheduler = LLMDailyReportScheduler(
        report_service=report_service,
    )

    assert scheduler.hour == 18
    assert scheduler.minute == 30