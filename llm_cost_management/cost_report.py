from collections import defaultdict
from datetime import datetime


class MonthlyCostReport:

    def __init__(self, records):

        self.records = records

    # --------------------------------------------------
    # Convert timestamp safely
    # --------------------------------------------------

    def _get_datetime(self, timestamp):

        # Already a datetime object
        if isinstance(timestamp, datetime):

            return timestamp

        # Timestamp loaded from JSON
        if isinstance(timestamp, str):

            try:

                return datetime.fromisoformat(
                    timestamp
                )

            except ValueError:

                return None

        return None

    # --------------------------------------------------
    # Cost by feature
    # --------------------------------------------------

    def cost_by_feature(self):

        result = defaultdict(float)

        for record in self.records:

            result[
                record["feature"]
            ] += record["cost_inr"]

        return {
            key: round(value, 4)
            for key, value in result.items()
        }

    # --------------------------------------------------
    # Cost by user
    # --------------------------------------------------

    def cost_by_user(self):

        result = defaultdict(float)

        for record in self.records:

            result[
                record["user_id"]
            ] += record["cost_inr"]

        return {
            key: round(value, 4)
            for key, value in result.items()
        }

    # --------------------------------------------------
    # Cost by month
    # --------------------------------------------------

    def cost_by_month(self):

        result = defaultdict(float)

        for record in self.records:

            timestamp = self._get_datetime(
                record["timestamp"]
            )

            # Skip invalid timestamps
            if timestamp is None:

                continue

            month = timestamp.strftime(
                "%Y-%m"
            )

            result[month] += (
                record["cost_inr"]
            )

        return {
            key: round(value, 4)
            for key, value in result.items()
        }

    # --------------------------------------------------
    # Generate complete report
    # --------------------------------------------------

    def generate_report(self):

        total_cost = sum(
            record["cost_inr"]
            for record in self.records
        )

        return {

            "total_cost_inr":
                round(total_cost, 4),

            "cost_by_feature":
                self.cost_by_feature(),

            "cost_by_user":
                self.cost_by_user(),

            "cost_by_month":
                self.cost_by_month()
        }