class BudgetMonitor:

    DAILY_BUDGET = 1000.0

    ALERT_THRESHOLDS = {
        0.50: "50% of daily LLM budget reached",
        0.80: "80% of daily LLM budget reached",
        1.00: "100% of daily LLM budget reached"
    }

    def __init__(self):
        self.current_cost = 0.0
        self.triggered_alerts = set()

    def add_cost(self, cost):

        self.current_cost += cost

        return self.check_budget()

    def check_budget(self):

        alerts = []

        usage_percentage = (
            self.current_cost /
            self.DAILY_BUDGET
        )

        for threshold, message in (
            self.ALERT_THRESHOLDS.items()
        ):

            if usage_percentage >= threshold:

                if threshold not in self.triggered_alerts:

                    alerts.append(message)

                    self.triggered_alerts.add(
                        threshold
                    )

        return alerts

    def get_current_cost(self):

        return round(
            self.current_cost,
            2
        )

    def get_remaining_budget(self):

        remaining = (
            self.DAILY_BUDGET -
            self.current_cost
        )

        return round(
            max(0, remaining),
            2
        )

    def is_budget_exceeded(self):

        return (
            self.current_cost >=
            self.DAILY_BUDGET
        )