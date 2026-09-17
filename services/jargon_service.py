import time

import sentry_sdk

from cache.redis_cache import RedisCache
from services.llm_client import LLMClient
from services.fallback_service import get_fallback_definition

from prompts.prompt_templates import (
    FINANCIAL_GUARDRAILS,
    JARGON_PROMPT,
)

from utils.languages import SUPPORTED_LANGUAGES
from utils.content_filter import check_content
from utils.logger import log_request
from utils.cost_tracker import calculate_cost, update_daily_cost


cache = RedisCache()
llm_client = LLMClient()


def get_jargon(term, language):
    """
    Generate a beginner-friendly explanation of a financial term
    in the language requested by the user.
    """

    # ------------------------------------------------------------
    # 1. Clean input
    # ------------------------------------------------------------

    term = term.strip()
    language = (language or "en").strip().lower()

    # ------------------------------------------------------------
    # 2. Support both language codes and language names
    # ------------------------------------------------------------

    language_aliases = {
        "english": "en",
        "hindi": "hi",
        "telugu": "te",
        "bengali": "bn",
        "tamil": "ta",
        "assamese": "as",
        "bodo": "brx",
        "dogri": "doi",
        "gujarati": "gu",
        "kannada": "kn",
        "kashmiri": "ks",
        "konkani": "gom",
        "maithili": "mai",
        "malayalam": "ml",
        "manipuri": "mni",
        "marathi": "mr",
        "nepali": "ne",
        "odia": "or",
        "punjabi": "pa",
        "sanskrit": "sa",
        "santali": "sat",
        "sindhi": "sd",
        "urdu": "ur",
    }

    language = language_aliases.get(language, language)

    # ------------------------------------------------------------
    # 3. Validate language
    # ------------------------------------------------------------

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    language_name = SUPPORTED_LANGUAGES[language]

    # ------------------------------------------------------------
    # 4. Cache
    #
    # v2 prevents old English responses from being returned
    # after the multilingual prompt change.
    # ------------------------------------------------------------

    cache_key = f"jargon:v2:{language}:{term.lower()}"

    try:
        cached = cache.get(cache_key)
    except Exception:
        cached = None

    if cached:
        return cached

    # ------------------------------------------------------------
    # 5. Build multilingual prompt
    # ------------------------------------------------------------

    prompt = JARGON_PROMPT.format(
        term=term,
        language_name=language_name,
        guardrails=FINANCIAL_GUARDRAILS,
    )

    started = time.monotonic()

    try:

        # --------------------------------------------------------
        # 6. Generate LLM response
        # --------------------------------------------------------

        llm_response = llm_client.generate_response(prompt)

        # --------------------------------------------------------
        # 7. Content filtering
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # 8. Cost tracking
        # --------------------------------------------------------

        token_usage = (
            len(prompt.split())
            + len(llm_response.split())
        )

        cost = calculate_cost(token_usage)

        update_daily_cost(cost)

        # --------------------------------------------------------
        # 9. Request logging
        # --------------------------------------------------------

        log_request(
            term,
            language,
            time.monotonic() - started,
            token_usage,
            cost,
        )

    except Exception as error:

        # --------------------------------------------------------
        # 10. Sentry logging
        # --------------------------------------------------------

        sentry_sdk.capture_exception(error)

        try:

            # ----------------------------------------------------
            # 11. Fallback response
            # ----------------------------------------------------

            response = get_fallback_definition(
                term,
                language,
            )

        except Exception as fallback_error:

            sentry_sdk.capture_exception(
                fallback_error
            )

            response = {
                "term": term,
                "language": language,
                "explanation": (
                    "This term is currently unavailable. "
                    "Please try again later."
                ),
            }

    # ------------------------------------------------------------
    # 12. Store response in cache
    # ------------------------------------------------------------

    cache.set(
        cache_key,
        response,
        expiry=3600,
    )

    return response