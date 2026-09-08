import logging
import os

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from middleware.auth_middleware import InternalAuthMiddleware
from routes import (
    fund_recommend,
    features,
    fraud_check,
    jargon,
    paper_trade_coach,
    portfolio,
)
from app.api.fund_recommend import router as fund_recommend_router
from app.api.languages import router as languages_router
from services.cache_warming import warm_cache
from services.catalogue_scheduler import start_catalogue_scheduler
from services.fund_catalogue import load_catalogue
from services.fraud_model import load_fraud_model

load_dotenv()

logging.basicConfig(level=logging.INFO)

sentry_dsn = os.getenv("SENTRY_DSN")

if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
    )

app = FastAPI(
    title="PaiseWise AI Service",
    version="2.0.0",
)

app.add_middleware(InternalAuthMiddleware)



def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-KEY",
        }
    }

    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if isinstance(operation, dict) and "responses" in operation:
                operation["security"] = [{"APIKeyHeader": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
async def startup_event():
    # Startup tasks are best-effort so a missing optional external dependency
    # does not make the HTTP process unavailable.

    # LLM-dependent cache warming is disabled by default during development.
    # Set ENABLE_LLM_WARMING=true in .env when you actually want to warm
    # the cache using the LLM.
    try:
        if os.getenv("ENABLE_LLM_WARMING", "false").lower() == "true":
            warm_cache()
        else:
            logging.info("LLM cache warming disabled")
    except Exception:
        logging.getLogger("ai-service").exception(
            "Jargon cache warming failed"
        )

    try:
        load_catalogue()
    except Exception:
        logging.getLogger("ai-service").exception(
            "Fund catalogue loading failed"
        )

    try:
        load_fraud_model()
    except Exception:
        logging.getLogger("ai-service").exception(
            "Fraud model loading failed"
        )

    try:
        start_catalogue_scheduler()
    except Exception:
        logging.getLogger("ai-service").exception(
            "Catalogue scheduler startup failed"
        )


app.include_router(jargon.router)
app.include_router(portfolio.router)
app.include_router(features.router)
app.include_router(fund_recommend_router)
app.include_router(fund_recommend.router)
app.include_router(paper_trade_coach.router)
app.include_router(fraud_check.router)
app.include_router(languages_router)


@app.get("/")
def health_check():
    return {"status": "AI service running"}


@app.get("/ai/health")
def ai_health():
    return {"status": "ok"}
