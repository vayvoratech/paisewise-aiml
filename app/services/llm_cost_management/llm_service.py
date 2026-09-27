import os

from google import genai

from app.utils.pii_scrubber import scrub_pii


class LLMService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    def generate_response(
        self,
        prompt,
        model
    ):

        # -----------------------------------------
        # PII protection
        # -----------------------------------------

        prompt = scrub_pii(prompt)

        # -----------------------------------------
        # Gemini API call
        # -----------------------------------------

        response = self.client.models.generate_content(
            model=model,
            contents=prompt
        )

        usage = response.usage_metadata

        input_tokens = (
            usage.prompt_token_count or 0
        )

        output_tokens = (
            usage.candidates_token_count or 0
        )

        thinking_tokens = (
            usage.thoughts_token_count or 0
        )

        total_tokens = (
            usage.total_token_count or 0
        )

        billable_output_tokens = (
            output_tokens +
            thinking_tokens
        )

        return {
            "response": response.text,
            "input_tokens": input_tokens,
            "output_tokens": billable_output_tokens,
            "thinking_tokens": thinking_tokens,
            "visible_output_tokens": output_tokens,
            "total_tokens": total_tokens
        }