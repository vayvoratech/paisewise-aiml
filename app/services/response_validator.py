import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ResponseValidationResult:
    """
    Result returned after validating an LLM response.

    valid:
        True  -> response is safe to return
        False -> response must not be returned

    message:
        Explanation when the response is rejected.
    """

    valid: bool
    message: str | None = None


# ---------------------------------------------------------
# Safe fallback response
# ---------------------------------------------------------

SAFE_FALLBACK_RESPONSE = (
    "I can provide general educational information about "
    "investments, but I can't provide personalized "
    "investment recommendations. Please consult a "
    "qualified financial professional for advice based "
    "on your individual situation."
)


# ---------------------------------------------------------
# Prohibited response patterns
# ---------------------------------------------------------
#
# These patterns are intentionally focused on direct
# personalized investment recommendations.
#
# They are checked after normalization so that variations
# in capitalization, whitespace, punctuation, etc. are
# handled.
# ---------------------------------------------------------

PROHIBITED_PATTERNS = (
    r"\byou\s+should\s+buy\b",
    r"\byou\s+should\s+sell\b",
    r"\byou\s+should\s+invest\b",

    r"\byou\s+must\s+buy\b",
    r"\byou\s+must\s+sell\b",
    r"\byou\s+must\s+invest\b",

    r"\bi\s+recommend\s+buying\b",
    r"\bi\s+recommend\s+selling\b",
    r"\bi\s+recommend\s+investing\b",

    r"\bi\s+recommend\s+that\s+you\s+buy\b",
    r"\bi\s+recommend\s+that\s+you\s+sell\b",
    r"\bi\s+recommend\s+that\s+you\s+invest\b",

    r"\byou\s+need\s+to\s+buy\b",
    r"\byou\s+need\s+to\s+sell\b",
    r"\byou\s+need\s+to\s+invest\b",

    r"\byou\s+ought\s+to\s+buy\b",
    r"\byou\s+ought\s+to\s+sell\b",

    # r"\bguaranteed\s+(?:profit|return|returns)\b",
    r"\bguaranteed\s+(?:a\s+)?(?:profit|return|returns)\b",
    r"\brisk[-\s]?free\s+(?:investment|return|profit)\b",

    r"\bguaranteed\s+to\s+(?:make|earn)\b",
)


# ---------------------------------------------------------
# Normalization
# ---------------------------------------------------------

def _normalize_response(response: str) -> str:
    """
    Normalize an LLM response before validation.

    Handles:
    - capitalization
    - repeated whitespace
    - newlines
    - tabs
    - surrounding whitespace
    - common punctuation variations
    """

    normalized = response.casefold()

    # Convert all whitespace sequences into one space.
    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    # Normalize common punctuation that can appear
    # between words.
    normalized = re.sub(
        r"[\u2010\u2011\u2012\u2013\u2014]",
        "-",
        normalized,
    )

    return normalized.strip()


# ---------------------------------------------------------
# Pattern matching
# ---------------------------------------------------------

def _contains_prohibited_content(
    normalized_response: str,
) -> bool:
    """
    Check whether the normalized response contains
    any prohibited recommendation pattern.
    """

    return any(
        re.search(
            pattern,
            normalized_response,
            flags=re.IGNORECASE,
        )
        for pattern in PROHIBITED_PATTERNS
    )


# ---------------------------------------------------------
# Public validator
# ---------------------------------------------------------

def validate_response(
    response: str,
) -> ResponseValidationResult:
    """
    Validate an LLM-generated response before returning it.

    Validation covers:

    - invalid response type
    - empty response
    - whitespace-only response
    - prohibited personalized recommendations
    - guaranteed-return language
    - risk-free investment claims
    - capitalization differences
    - repeated whitespace
    - newline/tab variations
    - common punctuation variations
    """

    # -----------------------------------------------------
    # Type validation
    # -----------------------------------------------------

    if not isinstance(response, str):
        raise TypeError(
            "response must be a string"
        )

    # -----------------------------------------------------
    # Empty response validation
    # -----------------------------------------------------

    if not response.strip():
        return ResponseValidationResult(
            valid=False,
            message="The generated response was empty.",
        )

    # -----------------------------------------------------
    # Normalize
    # -----------------------------------------------------

    normalized_response = _normalize_response(
        response
    )

    # -----------------------------------------------------
    # Prohibited content validation
    # -----------------------------------------------------

    if _contains_prohibited_content(
        normalized_response
    ):
        return ResponseValidationResult(
            valid=False,
            message=(
                "The generated response contained "
                "prohibited personalized investment "
                "advice."
            ),
        )

    # -----------------------------------------------------
    # Response is valid
    # -----------------------------------------------------

    return ResponseValidationResult(
        valid=True,
        message=None,
    )