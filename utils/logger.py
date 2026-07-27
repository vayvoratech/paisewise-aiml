import logging


logger = logging.getLogger("ai-service")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_request(
    term,
    language,
    response_time,
    token_usage=None,
    cost=None
):

    logger.info(
        f"""
Request Details:
Term: {term}
Language: {language}
Response Time: {response_time}s
Token Usage: {token_usage}
Cost: ₹{cost}
"""
    )