class LLMRouter:

    PREMIUM_MODEL = "gemini-3.6-flash"
    FREE_MODEL = "gemini-3.6-flash"

    LOW_PRIORITY_FEATURES = {
        "jargon",
        "faq",
        "general_education"
    }

    def select_model(
        self,
        user_tier,
        feature
    ):

        user_tier = user_tier.lower()
        feature = feature.lower()

        if user_tier == "premium":
            return self.PREMIUM_MODEL

        if user_tier == "free":
            return self.FREE_MODEL

        raise ValueError(
            "Invalid user tier"
        )