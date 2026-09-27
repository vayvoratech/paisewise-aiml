import re


def scrub_pii(text: str) -> str:
    if not isinstance(text, str):
        return text
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", "[EMAIL]", text)
    text = re.sub(r"\b\d{10}\b", "[PHONE]", text)
    return text
