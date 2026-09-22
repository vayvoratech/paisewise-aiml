import re


# ==================================================
# PII SCRUBBER
# ==================================================

def scrub_pii(text: str) -> str:
    """
    Detect and mask common Personally Identifiable
    Information (PII) before sending text to an LLM.

    Currently masks:
    - Email addresses
    - Indian phone numbers
    - PAN numbers
    - Aadhaar numbers
    """

    if not text:
        return text

    cleaned_text = text

    # --------------------------------------------------
    # 1. Email address
    # Example:
    # user@example.com
    # --------------------------------------------------

    cleaned_text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[REDACTED_EMAIL]",
        cleaned_text
    )

    # --------------------------------------------------
    # 2. Indian PAN
    # Example:
    # ABCDE1234F
    # --------------------------------------------------

    cleaned_text = re.sub(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        "[REDACTED_PAN]",
        cleaned_text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------
    # 3. Aadhaar
    # Example:
    # 1234 5678 9012
    # 123456789012
    # --------------------------------------------------

    cleaned_text = re.sub(
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "[REDACTED_AADHAAR]",
        cleaned_text
    )

    # --------------------------------------------------
    # 4. Indian phone number
    #
    # Examples:
    # 9876543210
    # +91 9876543210
    # +91-9876543210
    # 09876543210
    # --------------------------------------------------

    cleaned_text = re.sub(
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
        "[REDACTED_PHONE]",
        cleaned_text
    )

    return cleaned_text


# ==================================================
# SIMPLE TEST
# ==================================================

if __name__ == "__main__":

    test_text = """
    My name is Ravi Kumar.
    My email is ravi.kumar@example.com.
    My phone number is +91 9876543210.
    My PAN is ABCDE1234F.
    My Aadhaar number is 1234 5678 9012.

    Please explain mutual funds.
    """

    print("=" * 60)
    print("PII SCRUBBER TEST")
    print("=" * 60)

    print("\nOriginal text:")
    print(test_text)

    print("\nScrubbed text:")
    print(scrub_pii(test_text))