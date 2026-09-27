import hashlib
import json
import os
import time

import mlflow

from app.core.redis_cache import RedisCache
from app.prompts.portfolio_prompt import create_prompt
from app.services.llm_client import LLMClient


MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "file:./mlruns",
)

try:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("Portfolio Insight")
except Exception as error:
    print(
        "MLflow setup failed, continuing without tracking:",
        error,
    )
    mlflow = None


cache = RedisCache()
llm_client = LLMClient()


def _cache_key(user_id, language, portfolio_input):
    data = json.dumps(
        portfolio_input,
        sort_keys=True,
        default=str,
    )

    value = f"{user_id}:{language}:{data}"

    digest = hashlib.md5(
        value.encode("utf-8")
    ).hexdigest()

    return f"portfolio_insight:{user_id}:{language}:{digest}"


def _fallback_insight(language):
    messages = {
        "en": (
            "I could not generate the portfolio insight right now. "
            "Please try again later."
        ),
        "hi": (
            "अभी पोर्टफोलियो जानकारी तैयार नहीं हो सकी। "
            "कृपया बाद में फिर प्रयास करें।"
        ),
        "te": (
            "ప్రస్తుతం పోర్ట్‌ఫోలియో వివరాలను రూపొందించలేకపోయాను. "
            "దయచేసి కొంత సమయం తర్వాత ప్రయత్నించండి."
        ),
    }

    return messages.get(
        language,
        messages["en"],
    )


def generate_insight(user, holdings, market, language):
    start_time = time.time()

    prompt = create_prompt(
        user,
        holdings,
        market,
        language,
    )

    try:
        result = llm_client.generate_response(prompt)
    except Exception:
        return _fallback_insight(language)

    if mlflow is not None:
        try:
            with mlflow.start_run(
                run_name="Portfolio Insight"
            ):
                mlflow.log_param(
                    "user_id",
                    str(user.get("user_id", "")),
                )
                mlflow.log_param(
                    "language",
                    language,
                )
                mlflow.log_param(
                    "risk_profile",
                    user.get(
                        "risk_profile",
                        "",
                    ),
                )
                mlflow.log_text(
                    prompt,
                    "prompt.txt",
                )
                mlflow.log_text(
                    json.dumps(
                        holdings,
                        default=str,
                    ),
                    "holdings.json",
                )
                mlflow.log_text(
                    str(market),
                    "market.txt",
                )
                mlflow.log_metric(
                    "execution_time",
                    time.time() - start_time,
                )
                mlflow.log_metric(
                    "prompt_length",
                    len(prompt),
                )
                mlflow.log_metric(
                    "response_length",
                    len(result),
                )
                mlflow.log_text(
                    result,
                    "response.txt",
                )
        except Exception:
            pass

    return result


def get_portfolio_insight(
    portfolio_input: dict,
    language: str,
):
    language = (language or "en").lower()

    user_id = str(
        portfolio_input.get(
            "user_id",
            "",
        )
    ).strip()

    if not user_id:
        raise ValueError(
            "user_id is required"
        )

    key = _cache_key(
        user_id,
        language,
        portfolio_input,
    )

    cached = cache.get(key)

    if cached:
        return {
            "source": "cache",
            "insight": cached,
        }

    holdings = portfolio_input.get(
        "holdings",
        [],
    )

    market = portfolio_input.get(
        "market_context",
        {},
    )

    user = {
        "user_id": user_id,
        "full_name": portfolio_input.get(
            "full_name",
            "User",
        ),
        "age": portfolio_input.get(
            "age",
            "Not available",
        ),
        "risk_profile": portfolio_input.get(
            "risk_profile",
            "Not available",
        ),
        "monthly_investment": portfolio_input.get(
            "monthly_investment",
            "Not available",
        ),
    }

    try:
        result = generate_insight(
            user,
            holdings,
            market,
            language,
        )

        if result == _fallback_insight(language):
            return {
                "source": "fallback",
                "insight": result,
            }

        cache.set(
            key,
            result,
            expiry=86400,
        )

        return {
            "source": "llm",
            "insight": result,
        }

    except Exception:
        return {
            "source": "fallback",
            "insight": _fallback_insight(
                language
            ),
        }
