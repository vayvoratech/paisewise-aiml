# Gemini 3.6 Flash pricing
# Standard paid tier
# Pricing valid through December 31, 2026

USD_TO_INR = 95.71

GEMINI_INPUT_USD_PER_1M = 0.75

GEMINI_OUTPUT_USD_PER_1M = 3.75


def usd_per_million_to_inr_per_1k(
    usd_per_million
):
    """
    Convert USD per 1 million tokens
    into INR per 1,000 tokens.
    """

    usd_per_1k = (
        usd_per_million / 1_000_000
    ) * 1_000

    inr_per_1k = (
        usd_per_1k * USD_TO_INR
    )

    return round(
        inr_per_1k,
        6
    )


GEMINI_INPUT_INR_PER_1K = (
    usd_per_million_to_inr_per_1k(
        GEMINI_INPUT_USD_PER_1M
    )
)

GEMINI_OUTPUT_INR_PER_1K = (
    usd_per_million_to_inr_per_1k(
        GEMINI_OUTPUT_USD_PER_1M
    )
)


if __name__ == "__main__":

    print(
        "Gemini 3.6 Flash Pricing"
    )

    print(
        "USD to INR:",
        USD_TO_INR
    )

    print(
        "Input cost per 1K tokens:",
        GEMINI_INPUT_INR_PER_1K,
        "INR"
    )

    print(
        "Output cost per 1K tokens:",
        GEMINI_OUTPUT_INR_PER_1K,
        "INR"
    )