from datetime import datetime


class LLMCache:

    def __init__(self):
        self.cache = {}

    def _create_key(self, jargon_term):

        normalized_term = (
            jargon_term
            .strip()
            .lower()
        )

        current_hour = datetime.now().strftime(
            "%Y-%m-%d-%H"
        )

        return (
            f"{normalized_term}_{current_hour}"
        )

    def get(self, jargon_term):

        key = self._create_key(
            jargon_term
        )

        return self.cache.get(key)

    def set(
        self,
        jargon_term,
        response
    ):

        key = self._create_key(
            jargon_term
        )

        self.cache[key] = response

        return response

    def get_or_generate(
        self,
        jargon_term,
        generate_function
    ):

        cached_response = self.get(
            jargon_term
        )

        if cached_response is not None:

            return {
                "response": cached_response,
                "cached": True
            }

        response = generate_function()

        self.set(
            jargon_term,
            response
        )

        return {
            "response": response,
            "cached": False
        }