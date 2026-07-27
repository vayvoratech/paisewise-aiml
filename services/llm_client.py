import time
import logging


logger = logging.getLogger(__name__)


class LLMClient:

    def __init__(self):
        self.timeout = 30

    def generate_response(self, prompt):
        retries = 3

        for attempt in range(retries):
            try:
                response = "LLM response"

                return response

            except Exception as error:
                logger.exception(
                    f"LLM request failed on attempt {attempt + 1}: {error}"
                )

                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)

        raise Exception("LLM request failed after retries")