import logging
import os

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.auth_middleware import InternalAuthMiddleware
from app.api import (
    fund_recommend,
    features,
    fraud_check,
    jargon,
    paper_trade_coach,
    portfolio,
    stock_discovery,
    sip_coach,
    lesson_personalization,
    fraud_alerts,
    sip_scenarios,
)
from app.api.fund_recommend import router as fund_recommend_router
from app.api.languages import router as languages_router
from app.api.chat import router as chat_router
from app.api.churn import router as churn_router
from app.api.portfolio_analytics import router as portfolio_analytics_router
from app.api.portfolio_analytics_history import router as portfolio_history_router
from app.api.portfolio_comparison import router as portfolio_comparison_router
from app.api.portfolio_diversification import router as portfolio_diversification_router
from app.api.what_if import router as what_if_router
from app.api.market_context import router as market_context_router
from app.services.cache_warming import warm_cache
from app.services.catalogue_scheduler import start_catalogue_scheduler
from app.services.fund_catalogue import load_catalogue
from app.services.fraud_model import load_fraud_model

load_dotenv()
logging.basicConfig(level=logging.INFO)

sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
    )

app = FastAPI(title="PaiseWise AI Service", version="3.0.0")
app.add_middleware(InternalAuthMiddleware)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    schema.setdefault("components", {})["securitySchemes"] = {
        "APIKeyHeader": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}
    }
    for path in schema["paths"].values():
        for operation in path.values():
            if isinstance(operation, dict) and "responses" in operation:
                operation["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


@app.on_event("startup")
async def startup_event():
    try:
        if os.getenv("ENABLE_LLM_WARMING", "false").lower() == "true":
            warm_cache()
        else:
            logging.info("LLM cache warming disabled")
    except Exception:
        logging.getLogger("ai-service").exception("Jargon cache warming failed")
    try:
        load_catalogue()
    except Exception:
        logging.getLogger("ai-service").exception("Fund catalogue loading failed")
    try:
        load_fraud_model()
    except Exception:
        logging.getLogger("ai-service").exception("Fraud model loading failed")
    try:
        start_catalogue_scheduler()
    except Exception:
        logging.getLogger("ai-service").exception("Catalogue scheduler startup failed")


# Phase 1 / Phase 2 API surface.
for router in [
    jargon.router, portfolio.router, features.router, fund_recommend_router,
    fund_recommend.router, paper_trade_coach.router, fraud_check.router,
    languages_router, sip_coach.router, stock_discovery.router,
    lesson_personalization.router, fraud_alerts.router, sip_scenarios.router,
]:
    app.include_router(router)

# Phase 3 API surface.
for router in [
    chat_router, churn_router, portfolio_analytics_router,
    portfolio_history_router, portfolio_comparison_router,
    portfolio_diversification_router, what_if_router, market_context_router,
]:
    app.include_router(router)


@app.get("/")
def health_check():
    return {"status": "AI service running"}


@app.get("/ai/health")
def ai_health():
    return {"status": "ok"}
