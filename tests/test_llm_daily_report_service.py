from datetime import date
from unittest.mock import Mock

from app.services.llm_cost_service import LLMCostService
from app.services.llm_daily_report_service import LLMDailyReportService


def test_generate_daily_report_with_budget():
    repository = Mock()
    repository.get_daily_usage_summary.return_value = {
        "request_count": 2,
        "input_tokens": 1800,
        "output_tokens": 250,
        "total_tokens": 2050,
        "total_cost": 0.0006,
        "average_latency_ms": 1500.50,
        "model_count": 1,
    }

    cost_service = LLMCostService(
        input_cost_per_million=0.3,
        output_cost_per_million=2.5,
        daily_budget=0.001,
    )

    service = LLMDailyReportService(repository, cost_service)

    report = service.generate_report(date(2026, 9, 16))

    assert "AI Service Daily Cost & Performance Report" in report
    assert "Requests:          2" in report
    assert "Input Tokens:      1800" in report
    assert "Output Tokens:     250" in report
    assert "Total Tokens:      2050" in report
    assert "Total Cost:        $0.000600" in report
    assert "Daily Budget:      $0.001000" in report
    assert "Budget Used:       60.00%" in report
    assert "Budget Status:     Within Budget" in report
    assert "Average Latency:   1500.50 ms" in report


def test_generate_daily_report_when_budget_is_exceeded():
    repository = Mock()
    repository.get_daily_usage_summary.return_value = {
        "request_count": 5,
        "input_tokens": 3000,
        "output_tokens": 500,
        "total_tokens": 3500,
        "total_cost": 0.0015,
        "average_latency_ms": 2105.83,
        "model_count": 1,
    }

    cost_service = LLMCostService(
        input_cost_per_million=0.3,
        output_cost_per_million=2.5,
        daily_budget=0.001,
    )

    service = LLMDailyReportService(repository, cost_service)

    report = service.generate_report(date(2026, 9, 16))

    assert "Budget Used:       150.00%" in report
    assert "Budget Status:     Exceeded" in report
    assert "Average Latency:   2105.83 ms" in report


def test_generate_daily_report_without_latency():
    repository = Mock()
    repository.get_daily_usage_summary.return_value = {
        "request_count": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "average_latency_ms": None,
        "model_count": 0,
    }

    cost_service = LLMCostService(
        input_cost_per_million=0.3,
        output_cost_per_million=2.5,
        daily_budget=0.0,
    )

    service = LLMDailyReportService(repository, cost_service)

    report = service.generate_report(date(2026, 9, 16))

    assert "Requests:          0" in report
    assert "Average Latency:   N/A" in report
    assert "Budget Status:     Budget Not Configured" in report