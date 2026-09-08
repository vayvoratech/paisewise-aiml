from datetime import date
import logging
import threading

logger = logging.getLogger("ai-service.cost")
DAILY_BUDGET_INR = 500.0
# Configure these from the provider pricing before production use.
INPUT_COST_PER_1K_TOKENS_INR = 0.0
OUTPUT_COST_PER_1K_TOKENS_INR = 0.0

_lock = threading.Lock()
_day = date.today()
_daily_total = 0.0


def calculate_cost(token_usage: int, input_tokens: int | None = None, output_tokens: int | None = None) -> float:
    if input_tokens is None or output_tokens is None:
        return round(token_usage / 1000 * INPUT_COST_PER_1K_TOKENS_INR, 4)
    return round(
        input_tokens / 1000 * INPUT_COST_PER_1K_TOKENS_INR
        + output_tokens / 1000 * OUTPUT_COST_PER_1K_TOKENS_INR,
        4,
    )


def update_daily_cost(cost: float) -> float:
    global _day, _daily_total
    with _lock:
        today = date.today()
        if today != _day:
            _day, _daily_total = today, 0.0
        _daily_total += float(cost)
        if _daily_total >= DAILY_BUDGET_INR:
            logger.warning("Daily LLM budget alert: INR %.2f >= INR %.2f", _daily_total, DAILY_BUDGET_INR)
        return round(_daily_total, 4)


def get_daily_cost() -> float:
    global _day, _daily_total
    with _lock:
        today = date.today()
        if today != _day:
            _day, _daily_total = today, 0.0
        return round(_daily_total, 4)
