import time
import sentry_sdk

from app.core.redis_cache import RedisCache
from app.services.llm_client import LLMClient
from app.services.fallback_service import get_fallback_definition
from app.prompts.prompt_templates import (
    FINANCIAL_GUARDRAILS,
    JARGON_PROMPT_ENGLISH,
    JARGON_PROMPT_HINDI,
)
from app.utils.languages import SUPPORTED_LANGUAGES
from app.utils.content_filter import check_content
from app.utils.logger import log_request
from app.utils.cost_tracker import calculate_cost, update_daily_cost

cache = RedisCache()
llm_client = LLMClient()


def _normalize_language(language):
    value = (language or "en").strip().lower()

    # Accept language codes directly.
    if value in SUPPORTED_LANGUAGES:
        return value

    # Accept full language names such as "Kannada", "Telugu", etc.
    for code, name in SUPPORTED_LANGUAGES.items():
        if value == name.lower():
            return code

    # Keep existing fallback behavior for unsupported languages.
    return "en"


def _build_jargon_prompt(term, language):
    language_name = SUPPORTED_LANGUAGES[language]

    if language == "hi":
        return JARGON_PROMPT_HINDI.format(
            term=term,
            language_name=language_name,
            guardrails=FINANCIAL_GUARDRAILS,
        )

    # The existing English template contains "English" explicitly.
    # Replace that instruction with the requested language.
    prompt_template = JARGON_PROMPT_ENGLISH.replace(
        "plain, beginner-friendly English",
        f"plain, beginner-friendly {language_name}",
    )

    prompt = prompt_template.format(
        term=term,
        language_name=language_name,
        guardrails=FINANCIAL_GUARDRAILS,
    )

    prompt += (
        f"\nRespond completely in {language_name}. "
        "Do not switch to English unless the requested language is English."
    )

    return prompt


def get_jargon(term, language):
    term = term.strip()
    language = _normalize_language(language)

    cache_key = f"jargon:{language}:{term.lower()}"

    try:
        cached = cache.get(cache_key)
    except Exception:
        cached = None

    if cached:
        return cached

    prompt = _build_jargon_prompt(term, language)

    started = time.monotonic()

    try:
        llm_response = llm_client.generate_response(prompt)

        filtered = check_content(llm_response)

        response = {
            "term": term,
            "language": language,
            "explanation": (
                filtered["message"]
                if filtered["blocked"]
                else filtered["content"]
            ),
        }

        token_usage = len(prompt.split()) + len(llm_response.split())
        cost = calculate_cost(token_usage)
        update_daily_cost(cost)

        log_request(
            term,
            language,
            time.monotonic() - started,
            token_usage,
            cost,
        )

    except Exception as error:
        sentry_sdk.capture_exception(error)

        try:
            response = get_fallback_definition(term, language)

        except Exception as fallback_error:
            sentry_sdk.capture_exception(fallback_error)

            response = {
                "term": term,
                "language": language,
                "explanation": (
                    "This term is currently unavailable. "
                    "Please try again later."
                ),
            }

    cache.set(cache_key, response, expiry=3600)

    return response
