from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class FraudWeeklySummary:
    start_date: datetime
    end_date: datetime
    flagged_cases: int
    reviewed_cases: int
    true_fraud_cases: int
    false_positive_cases: int
    true_positive_rate: float | None


class FraudWeeklySummaryService:
    """Builds a weekly fraud summary from fraud-case records."""

    def build_summary(
        self,
        fraud_cases: list[dict],
        *,
        end_date: datetime | None = None,
    ) -> FraudWeeklySummary:
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        start_date = end_date - timedelta(days=7)

        weekly_cases = []

        for case in fraud_cases:
            created_at = case.get("created_at")

            if created_at is None:
                raise ValueError(
                    "Fraud case is missing created_at"
                )

            if created_at.tzinfo is None:
                created_at = created_at.replace(
                    tzinfo=timezone.utc
                )

            if start_date <= created_at <= end_date:
                weekly_cases.append(case)

        flagged_cases = len(weekly_cases)

        true_fraud_cases = sum(
            1
            for case in weekly_cases
            if case.get("reviewer_decision") == "TRUE_FRAUD"
        )

        false_positive_cases = sum(
            1
            for case in weekly_cases
            if case.get("reviewer_decision") == "FALSE_POSITIVE"
        )

        reviewed_cases = (
            true_fraud_cases + false_positive_cases
        )

        if reviewed_cases == 0:
            true_positive_rate = None
        else:
            true_positive_rate = (
                true_fraud_cases / reviewed_cases
            )

        return FraudWeeklySummary(
            start_date=start_date,
            end_date=end_date,
            flagged_cases=flagged_cases,
            reviewed_cases=reviewed_cases,
            true_fraud_cases=true_fraud_cases,
            false_positive_cases=false_positive_cases,
            true_positive_rate=true_positive_rate,
        )