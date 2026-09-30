from app.services.fraud_weekly_summary_service import FraudWeeklySummary


class FraudWeeklyReportFormatter:
    """Formats the weekly fraud summary for operational reporting."""

    def format(self, summary: FraudWeeklySummary) -> str:
        if summary.true_positive_rate is None:
            true_positive_rate = "N/A"
        else:
            true_positive_rate = (
                f"{summary.true_positive_rate * 100:.2f}%"
            )

        return (
            "🚨 Weekly Fraud Summary\n\n"
            f"Period: "
            f"{summary.start_date.isoformat()} "
            f"to "
            f"{summary.end_date.isoformat()}\n\n"
            f"Flagged cases: {summary.flagged_cases}\n"
            f"Reviewed cases: {summary.reviewed_cases}\n"
            f"True fraud cases: {summary.true_fraud_cases}\n"
            f"False positives: {summary.false_positive_cases}\n"
            f"True-positive rate: {true_positive_rate}"
        )