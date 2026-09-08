import logging

logger = logging.getLogger("ai-service")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def log_request(term, language, response_time, token_usage=None, cost=None):
    logger.info(
        "ai_request term=%s language=%s response_time=%.3fs token_usage=%s cost_inr=%.4f",
        term, language, response_time, token_usage, cost or 0.0,
    )
