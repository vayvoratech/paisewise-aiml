import time
import sentry_sdk

from cache.redis_cache import RedisCache
from services.llm_client import LLMClient
from services.fallback_service import get_fallback_definition
from prompts.prompt_templates import (
    FINANCIAL_GUARDRAILS,
    JARGON_PROMPT_ENGLISH,
    JARGON_PROMPT_HINDI,
)
from utils.languages import SUPPORTED_LANGUAGES
from utils.content_filter import check_content
from utils.logger import log_request
from utils.cost_tracker import calculate_cost, update_daily_cost

cache = RedisCache()
llm_client = LLMClient()


def get_jargon(term, language):
    term = term.strip()
    language = (language or "en").strip().lower()
    language_aliases = {"english": "en", "hindi": "hi", "telugu": "te", "marathi": "mr"}
    language = language_aliases.get(language, language)
    if language not in SUPPORTED_LANGUAGES:
        language = "en"
    cache_key = f"jargon:{language}:{term.lower()}"

    try:
        cached = cache.get(cache_key)
    except Exception:
        cached = None
    if cached:
        return cached

    prompt_template = JARGON_PROMPT_HINDI if language == "hi" else JARGON_PROMPT_ENGLISH
    prompt = prompt_template.format(
        term=term,
        language_name=SUPPORTED_LANGUAGES[language],
        guardrails=FINANCIAL_GUARDRAILS,
    )
    started = time.monotonic()
    try:
        llm_response = llm_client.generate_response(prompt)
        filtered = check_content(llm_response)
        response = {
            "term": term,
            "language": language,
            "explanation": filtered["message"] if filtered["blocked"] else filtered["content"],
        }
        token_usage = len(prompt.split()) + len(llm_response.split())
        cost = calculate_cost(token_usage)
        update_daily_cost(cost)
        log_request(term, language, time.monotonic() - started, token_usage, cost)
    except Exception as error:
        sentry_sdk.capture_exception(error)
        try:
            response = get_fallback_definition(term, language)
        except Exception as fallback_error:
            sentry_sdk.capture_exception(fallback_error)
            response = {
                "term": term,
                "language": language,
                "explanation": "This term is currently unavailable. Please try again later.",
            }

    cache.set(cache_key, response, expiry=3600)
    return response
