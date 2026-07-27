from cache.redis_cache import RedisCache
from services.context_assembly import assemble_portfolio_context
from services.llm_client import LLMClient

from prompts.prompt_templates import (
    ENGLISH_PORTFOLIO_PROMPT,
    HINDI_PORTFOLIO_PROMPT
)

from services.portfolio_fallback import get_portfolio_fallback


cache = RedisCache()
llm_client = LLMClient()
def validate_insight_quality(response: str):

    word_count = len(response.split())

    return 50 <= word_count <= 200

def get_portfolio_insight(user_id: str, language: str):

    cache_key = f"portfolio_insight:{user_id}"

    # Step 1: Check daily cache
    cached_result = cache.get(cache_key)

    if cached_result:
        return {
            "source": "cache",
            "insight": cached_result
        }


    try:

        # Step 2: Build portfolio context
        portfolio_context = assemble_portfolio_context(user_id)


        # Step 3: Select language prompt
        if language.lower() == "hindi":
            prompt = HINDI_PORTFOLIO_PROMPT.format(
                portfolio_context=portfolio_context
            )

        else:
            prompt = ENGLISH_PORTFOLIO_PROMPT.format(
                portfolio_context=portfolio_context
            )


        # Step 4: Call existing LLM wrapper
        response = llm_client.generate_response(prompt)


        # Step 5: Validate insight quality before storing
        if validate_insight_quality(response):

            cache.set(
                cache_key,
                response,
                expiry=86400
            )

        else:

            response = get_portfolio_fallback()


        return {
            "source": "llm",
            "insight": response
        }


    except Exception:

        return {
            "source": "fallback",
            "insight": get_portfolio_fallback()
        }