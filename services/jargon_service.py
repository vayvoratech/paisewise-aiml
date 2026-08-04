import time

from cache.redis_cache import RedisCache
from services.llm_client import LLMClient
from services.fallback_service import get_fallback_definition
from prompts.prompt_templates import (
    JARGON_PROMPT,
    FINANCIAL_GUARDRAILS
)

from utils.languages import SUPPORTED_LANGUAGES
from utils.content_filter import check_content
from utils.logger import log_request
from utils.cost_tracker import (
    calculate_cost,
    update_daily_cost
)

cache = RedisCache()
llm_client = LLMClient()


def get_jargon(term, language):

    cache_key = f"jargon:{language}:{term.lower()}"

    # 1. Check Redis cache
    cached_result = cache.get(cache_key)

    if cached_result:
        print("CACHE HIT:", cache_key)
        return cached_result

    print("CACHE MISS:", cache_key)

    # 2. Validate language

    language = language.lower()

    if language not in SUPPORTED_LANGUAGES:
        language = "en"


    language_name = SUPPORTED_LANGUAGES[language]


    # Build dynamic prompt

    prompt = JARGON_PROMPT.format(
        term=term,
        language_name=language_name,
        guardrails=FINANCIAL_GUARDRAILS
    )

    try:

        start_time = time.time()

        llm_response = llm_client.generate_response(prompt)

        filtered_response = check_content(llm_response)

        if filtered_response["blocked"]:

            response = {
                "term": term,
                "language": language,
                "explanation": filtered_response["message"]
            }

        else:

            response = {
                "term": term,
                "language": language,
                "explanation": filtered_response["content"]
            }

        response_time = round(
            time.time() - start_time,
            2
        )

        # Temporary token estimation
        # Replace with actual token usage when a real LLM is integrated.
        token_usage = len(prompt.split()) + len(llm_response.split())

        cost = calculate_cost(token_usage)

        update_daily_cost(cost)

        log_request(
            term,
            language,
            response_time,
            token_usage,
            cost
        )

    except Exception:

        fallback_response = get_fallback_definition(term)

        response = fallback_response

    # 3. Store response in Redis
    cache.set(
        cache_key,
        response,
        expiry=3600
    )

    return response