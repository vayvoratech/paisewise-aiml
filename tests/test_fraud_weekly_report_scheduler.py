from unittest.mock import MagicMock

import pytest

from app.services.fraud_weekly_report_scheduler import (
    FraudWeeklyReportScheduler,
)


def test_scheduler_uses_explicit_schedule_values():
    report_service = MagicMock()

    scheduler = FraudWeeklyReportScheduler(
        report_service=report_service,
        day_of_week="friday",
        hour=14,
        minute=30,
    )

    assert scheduler.day_of_week == "friday"
    assert scheduler.hour == 14
    assert scheduler.minute == 30


def test_send_weekly_report_calls_report_service():
    report_service = MagicMock()

    scheduler = FraudWeeklyReportScheduler(
        report_service=report_service,
    )

    scheduler.send_weekly_report()

    report_service.send.assert_called_once_with()


def test_invalid_hour_is_rejected():
    report_service = MagicMock()

    with pytest.raises(
        ValueError,
        match="hour must be between 0 and 23",
    ):
        FraudWeeklyReportScheduler(
            report_service=report_service,
            hour=24,
        )


def test_invalid_minute_is_rejected():
    report_service = MagicMock()

    with pytest.raises(
        ValueError,
        match="minute must be between 0 and 59",
    ):
        FraudWeeklyReportScheduler(
            report_service=report_service,
            minute=60,
        )


def test_empty_day_of_week_is_rejected():
    report_service = MagicMock()

    with pytest.raises(
        ValueError,
        match="day_of_week cannot be empty",
    ):
        FraudWeeklyReportScheduler(
            report_service=report_service,
            day_of_week="   ",
        )


def test_start_registers_weekly_job():
    report_service = MagicMock()

    scheduler = FraudWeeklyReportScheduler(
        report_service=report_service,
        day_of_week="monday",
        hour=9,
        minute=0,
    )

    scheduler.start()

    try:
        jobs = scheduler.scheduler.get_jobs()

        assert len(jobs) == 1
        assert jobs[0].id == "fraud_weekly_report"

    finally:
        scheduler.shutdown()