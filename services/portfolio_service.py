import json
import logging
import os
from datetime import date, datetime, time as dt_time, timedelta

from dotenv import load_dotenv

load_dotenv()

try:
    import mlflow
except ImportError:
    mlflow = None

from cache.redis_cache import RedisCache
from prompts.prompt_templates import FINANCIAL_GUARDRAILS, PORTFOLIO_PROMPT
from services.context_assembly import assemble_portfolio_context
from services.llm_client import LLMClient
from services.portfolio_fallback import get_portfolio_fallback
from utils.languages import SUPPORTED_LANGUAGES
from utils.cost_tracker import calculate_cost, update_daily_cost
from utils.logger import log_request


logger = logging.getLogger("ai-service.portfolio")
cache = RedisCache()
llm_client = LLMClient()


# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

if mlflow is not None:
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment("Portfolio Insight")
        logger.info(
            "MLflow tracking enabled: %s",
            MLFLOW_TRACKING_URI,
        )
    except Exception as error:
        logger.warning(
            "MLflow setup failed; continuing without tracking: %s",
            error,
        )
        mlflow = None


def _seconds_until_midnight() -> int:
    now = datetime.now().astimezone()
    tomorrow = datetime.combine(
        now.date() + timedelta(days=1),
        dt_time.min,
        tzinfo=now.tzinfo,
    )
    return max(1, int((tomorrow - now).total_seconds()))


def _cache_key(user_id: str, language: str) -> str:
    # Date is part of the key; language prevents cross-language responses.
    return f"portfolio_insight:{user_id}:{date.today().isoformat()}:{language}"


def validate_insight_quality(response: str) -> bool:
    words = len(response.split())
    return 50 <= words <= 200


def get_portfolio_insight(portfolio_input: dict, language: str):
    language = (language or "en").lower()

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    user_id = str(portfolio_input.get("user_id", "")).strip()

    if not user_id:
        raise ValueError("user_id is required")

    key = _cache_key(user_id, language)

    cached = cache.get(key)

    # Backward-compatible lookup for old cache entries.
    if not cached:
        cached = cache.get(
            f"portfolio_insight:{user_id}:{language}"
        )

    if cached:
        return {
            "source": "cache",
            "insight": cached,
        }

    context = assemble_portfolio_context(portfolio_input)

    language_name = SUPPORTED_LANGUAGES[language]

    prompt = PORTFOLIO_PROMPT.format(
        portfolio_context=context,
        language_name=language_name,
        guardrails=FINANCIAL_GUARDRAILS,
    )

    mlflow_run_started = False

    try:
        started = datetime.now().timestamp()

        # Start MLflow run.
        if mlflow is not None:
            try:
                mlflow.start_run(
                    run_name="Portfolio Insight"
                )
                mlflow_run_started = True

                mlflow.log_param(
                    "user_id",
                    user_id,
                )

                mlflow.log_param(
                    "language",
                    language,
                )

                mlflow.log_text(
                    prompt,
                    "prompt.txt",
                )

                mlflow.log_text(
                    json.dumps(
                        portfolio_input,
                        default=str,
                    ),
                    "portfolio_input.json",
                )

            except Exception as tracking_error:
                logger.warning(
                    "MLflow run setup failed; continuing without tracking: %s",
                    tracking_error,
                )

        # Generate LLM response.
        response = llm_client.generate_response(prompt).strip()

        token_usage = (
            len(prompt.split())
            + len(response.split())
        )

        cost = calculate_cost(token_usage)

        update_daily_cost(cost)

        response_time = (
            datetime.now().timestamp() - started
        )

        log_request(
            "portfolio-insight",
            language,
            response_time,
            token_usage,
            cost,
        )

        if not validate_insight_quality(response):
            raise ValueError(
                "LLM response failed the 50-200 word quality check"
            )

        # Log successful request to MLflow.
        if mlflow is not None and mlflow_run_started:
            try:
                mlflow.log_metric(
                    "execution_time",
                    response_time,
                )

                mlflow.log_metric(
                    "prompt_length",
                    len(prompt),
                )

                mlflow.log_metric(
                    "response_length",
                    len(response),
                )

                mlflow.log_metric(
                    "token_usage",
                    token_usage,
                )

                mlflow.log_text(
                    response,
                    "response.txt",
                )

            except Exception as tracking_error:
                logger.warning(
                    "MLflow logging failed: %s",
                    tracking_error,
                )

        cache.set(
            key,
            response,
            expiry=_seconds_until_midnight(),
        )

        return {
            "source": "llm",
            "insight": response,
        }

    except Exception as error:
        logger.exception(
            "Portfolio insight generation failed: %s",
            error,
        )

        market = context.get("market_context") or {}

        return {
            "source": "fallback",
            "insight": get_portfolio_fallback(
                market.get(
                    "daily_change_pct",
                    market.get("dailyChangePct"),
                )
            ),
        }

    finally:
        if mlflow is not None and mlflow_run_started:
            try:
                mlflow.end_run()
            except Exception as tracking_error:
                logger.warning(
                    "MLflow run close failed: %s",
                    tracking_error,
                )
