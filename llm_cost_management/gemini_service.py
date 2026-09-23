from google import genai
import os

from .circuit_breaker import CircuitBreaker, CircuitBreakerOpen
from src.pii_scrubber import scrub_pii


class GeminiService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.6-flash"

        # -----------------------------------------
        # Circuit breaker configuration
        # -----------------------------------------

        self.circuit_breaker = CircuitBreaker(
            error_threshold=0.10,       # More than 10% errors
            window_size=20,             # Track latest 20 calls
            recovery_timeout=300        # 5 minutes
        )

        # -----------------------------------------
        # Static fallback response
        # -----------------------------------------

        self.static_fallback = (
            "AI service is temporarily unavailable. "
            "Please try again shortly."
        )

    def generate_response(self, prompt):

        # -----------------------------------------
        # 1. Scrub PII before Gemini call
        # -----------------------------------------

        prompt = scrub_pii(prompt)

        # -----------------------------------------
        # 2. Check circuit breaker
        # -----------------------------------------

        if not self.circuit_breaker.allow_request():

            status = self.circuit_breaker.get_status()

            return {
                "text": self.static_fallback,
                "model": "fallback",
                "fallback": True,
                "reason": "circuit_breaker_open",
                "circuit_state": status["state"]
            }

        # -----------------------------------------
        # 3. Call Gemini
        # -----------------------------------------

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            # -----------------------------------------
            # 4. Successful API call
            # -----------------------------------------

            self.circuit_breaker.record_success()

            return {
                "text": response.text,
                "model": self.model,
                "fallback": False,
                "circuit_state":
                    self.circuit_breaker.get_status()["state"]
            }

        except Exception as e:

            self.circuit_breaker.record_failure()

            print(
                "GEMINI API ERROR:",
                repr(e)
            )

            status = self.circuit_breaker.get_status()

            return {
                "text": self.static_fallback,
                "model": "fallback",
                "fallback": True,
                "reason": "llm_api_error",
                "error": str(e),
                "circuit_state": status["state"]
            }

    def get_circuit_status(self):
        """Return circuit breaker status."""

        return self.circuit_breaker.get_status()


if __name__ == "__main__":

    service = GeminiService()

    result = service.generate_response(
        "Explain diversification in investing in one simple sentence."
    )

    print(
        "Model:",
        result["model"]
    )

    print(
        "Response:",
        result["text"]
    )

    print(
        "Fallback:",
        result.get("fallback")
    )

    print(
        "Circuit State:",
        result.get("circuit_state")
    )