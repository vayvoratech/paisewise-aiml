import json
import time

try:
    import mlflow
except ImportError:  # Keep unit-test collection independent of MLflow installation.
    mlflow = None

from app.prompts.portfolio_prompt import create_prompt
from app.services.llm_service import generate_portfolio_response


if mlflow is not None:
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("Portfolio Insight")


def generate_insight(user, holdings, market, language):
    start_time = time.time()

    prompt = create_prompt(
        user,
        holdings,
        market,
        language,
    )

    if mlflow is None:
        # MLflow is required for production tracking. The fallback keeps the
        # application importable for local unit tests when MLflow is absent.
        return generate_portfolio_response(prompt)

    with mlflow.start_run(run_name="Portfolio Insight"):
        mlflow.log_param("user_id", str(user.get("user_id", "")))
        mlflow.log_param("language", language)
        mlflow.log_param("risk_profile", user.get("risk_profile", ""))

        mlflow.log_text(prompt, "prompt.txt")
        mlflow.log_text(json.dumps(holdings, default=str), "holdings.json")
        mlflow.log_text(str(market), "market.txt")

        result = generate_portfolio_response(prompt)

        mlflow.log_metric("execution_time", time.time() - start_time)
        mlflow.log_metric("prompt_length", len(prompt))
        mlflow.log_metric("response_length", len(result))
        mlflow.log_text(result, "response.txt")

    return result
