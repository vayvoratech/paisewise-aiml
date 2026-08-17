from app.config.settings import GEMINI_API_KEY, GEMINI_MODEL
from app.prompts.financial_prompt import build_financial_prompt


def _get_client():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    from google import genai

    return genai.Client(api_key=GEMINI_API_KEY)


def _check_model():
    if not GEMINI_MODEL:
        raise RuntimeError("GEMINI_MODEL is not set.")


def generate_response(term: str, language: str) -> str:
    _check_model()

    prompt = build_financial_prompt(term, language)
    response = _get_client().models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return response.text or ""


def generate_portfolio_response(prompt: str) -> str:
    safety_words = [
        "guarantee",
        "guaranteed return",
        "100% return",
        "double my money",
        "multibagger",
        "sure shot",
        "tomorrow stock",
    ]

    blocked_inputs = [
        "ignore previous instructions",
        "forget previous instructions",
        "system prompt",
        "act as",
        "jailbreak",
        "bypass",
        "developer mode",
        "reveal your prompt",
        "ignore all rules",
    ]

    text = prompt.lower()

    if any(word in text for word in safety_words):
        return (
            "I can provide financial education and portfolio insights, "
            "but I cannot guarantee returns or predict future stock prices."
        )

    if any(word in text for word in blocked_inputs):
        return "This request cannot be processed because it violates the application safety policy."

    _check_model()

    response = _get_client().models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return response.text or ""
