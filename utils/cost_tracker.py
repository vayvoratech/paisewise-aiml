"""
Cost tracking utility.

NOTE:
This implementation uses an estimated token cost because the current
LLMClient is a placeholder and does not return real token usage.

Replace COST_PER_TOKEN_INR and token usage with actual LLM pricing
when a production LLM is integrated.
"""

DAILY_BUDGET_INR = 500.0
COST_PER_TOKEN_INR = 0.001  # Placeholder value

daily_total_cost = 0.0


def calculate_cost(token_usage: int) -> float:
    """Calculate estimated cost for one LLM call."""
    return round(token_usage * COST_PER_TOKEN_INR, 2)


def update_daily_cost(cost: float) -> float:
    """Add cost to today's running total."""

    global daily_total_cost

    daily_total_cost += cost

    if daily_total_cost >= DAILY_BUDGET_INR:
        print(
            f"WARNING: Daily LLM budget exceeded! Total: ₹{daily_total_cost:.2f}"
        )

    return round(daily_total_cost, 2)