"""Small Gemini wrapper with timeout, retry and structured logging."""

import concurrent.futures
import logging
import os
import time

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("ai-service.llm")


class LLMClient:
    def __init__(self, timeout: float = 30.0, retries: int = 3):
        self.timeout = timeout
        self.retries = retries
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = None

    def _get_client(self):
        if self._client is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY not found")
            from google import genai
            self._client = genai.Client(api_key=api_key)
        return self._client

    def _call(self, prompt: str):
        response = self._get_client().models.generate_content(
            model=self.model,
            contents=prompt,
        )
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return text.strip()

    def generate_response(self, prompt: str) -> str:
        last_error = None
        for attempt in range(1, self.retries + 1):
            started = time.monotonic()
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self._call, prompt)
                    return future.result(timeout=self.timeout)
            except Exception as error:
                last_error = error
                elapsed = time.monotonic() - started
                logger.warning(
                    "LLM request failed attempt=%s/%s elapsed=%.2fs error=%s",
                    attempt, self.retries, elapsed, error,
                )
                if attempt < self.retries:
                    time.sleep(2 ** (attempt - 1))
        raise RuntimeError(f"LLM request failed after {self.retries} retries: {last_error}") from last_error
