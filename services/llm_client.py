import time
import logging
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

logger = logging.getLogger(__name__)


class LLMClient:

    def __init__(self):

        self.timeout = 30

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise Exception("GEMINI_API_KEY not found")

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "models/gemini-flash-latest"


    def generate_response(self, prompt):

        retries = 3

        for attempt in range(retries):

            try:

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )

                return response.text


            except Exception as error:

                logger.exception(
                    f"LLM request failed on attempt {attempt + 1}: {error}"
                )

                if attempt < retries - 1:

                    wait_time = 2 ** attempt
                    time.sleep(wait_time)


        raise Exception("LLM request failed after retries")