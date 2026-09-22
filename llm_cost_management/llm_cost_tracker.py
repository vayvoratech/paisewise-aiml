from datetime import datetime


class LLMCostTracker:

    def __init__(self):
        self.records = []

    def calculate_cost(
        self,
        input_tokens,
        output_tokens,
        input_cost_per_1k,
        output_cost_per_1k
    ):
        input_cost = (
            input_tokens / 1000
        ) * input_cost_per_1k

        output_cost = (
            output_tokens / 1000
        ) * output_cost_per_1k

        total_cost = (
            input_cost +
            output_cost
        )

        return round(
            total_cost,
            4
        )

    def track_usage(
        self,
        user_id,
        user_tier,
        feature,
        model,
        input_tokens,
        output_tokens,
        thinking_tokens,
        cost_inr
    ):

        total_tokens = (
            input_tokens
            + output_tokens
            + thinking_tokens
        )

        record = {
            "timestamp": datetime.now(),

            "user_id": user_id,

            "user_tier": user_tier,

            "feature": feature,

            "model": model,

            "input_tokens": input_tokens,

            "output_tokens": output_tokens,

            "thinking_tokens": thinking_tokens,

            "total_tokens": total_tokens,

            "cost_inr": cost_inr
        }

        self.records.append(
            record
        )

        return record

    def _get_datetime(
        self,
        timestamp
    ):

        if isinstance(
            timestamp,
            datetime
        ):
            return timestamp

        if isinstance(
            timestamp,
            str
        ):
            try:
                return datetime.fromisoformat(
                    timestamp
                )
            except ValueError:
                return None

        return None

    def get_total_cost(self):

        return round(
            sum(
                record["cost_inr"]
                for record in self.records
            ),
            4
        )

    def get_cost_by_feature(self):

        result = {}

        for record in self.records:

            feature = record["feature"]

            result[feature] = (
                result.get(feature, 0)
                + record["cost_inr"]
            )

        return {
            key: round(
                value,
                4
            )
            for key, value in result.items()
        }

    def get_cost_by_user_tier(self):

        result = {}

        for record in self.records:

            tier = record["user_tier"]

            result[tier] = (
                result.get(tier, 0)
                + record["cost_inr"]
            )

        return {
            key: round(
                value,
                4
            )
            for key, value in result.items()
        }

    def get_cost_by_day(self):

        result = {}

        for record in self.records:

            timestamp = self._get_datetime(
                record["timestamp"]
            )

            if timestamp is None:
                continue

            day = timestamp.strftime(
                "%Y-%m-%d"
            )

            result[day] = (
                result.get(day, 0)
                + record["cost_inr"]
            )

        return {
            key: round(
                value,
                4
            )
            for key, value in result.items()
        }