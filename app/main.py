<<<<<<< HEAD
from main import app

__all__ = ["app"]
=======
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI  # pyright: ignore[reportMissingImports]

from app.core.redis import redis_client
from app.services.fraud_startup_service import FraudStartupService
from app.services.fraud_weekly_report_notification_service import (
    FraudWeeklyReportNotificationService,
)
from app.services.fraud_weekly_report_scheduler import (
    FraudWeeklyReportScheduler,
)
from app.services.fund_recommendation_audit_report_service import (
    FundRecommendationAuditReportService,
)
from app.services.fund_recommendation_audit_scheduler import (
    FundRecommendationAuditScheduler,
)
from app.services.rag.rag_service import RAGService

from app.api.routes.chat import (  # pyright: ignore[reportMissingImports]
    configure_rag_service,
    prewarm_rag_cache,
    router as chat_router,
)
from app.api.routes.chat_jobs import (
    ChatJobWorker,
    router as chat_jobs_router,
)
from app.api.routes.portfolio_analytics import (  # pyright: ignore[reportMissingImports]
    router as portfolio_analytics_router,
)
from app.api.routes.what_if import (  # pyright: ignore[reportMissingImports]
    router as what_if_router,
)
from app.api.routes.portfolio_analytics_history import (  # pyright: ignore[reportMissingImports]
    router as portfolio_analytics_history_router,
)
from app.api.routes.portfolio_comparison import (  # pyright: ignore[reportMissingImports]
    router as portfolio_comparison_router,
)
from app.api.routes.churn import (  # pyright: ignore[reportMissingImports]
    router as churn_router,
)
from app.api.routes.market_context import (  # pyright: ignore[reportMissingImports]
    router as market_context_router,
)
from app.api.routes.stock_news import (  # pyright: ignore[reportMissingImports]
    router as stock_news_router,
)
from app.api.routes.sector_news import (  # pyright: ignore[reportMissingImports]
    router as sector_news_router,
)
from app.api.routes.stock_discovery import (  # pyright: ignore[reportMissingImports]
    router as stock_discovery_router,
)

from app.api.routes.fraud import router as fraud_router
from app.api.routes.fraud_cases import router as fraud_cases_router
from app.api.routes.fund_recommendation import (
    router as fund_recommendation_router,
)


ENABLE_BACKGROUND_SCHEDULERS = (
    os.getenv("ENABLE_BACKGROUND_SCHEDULERS", "true").lower()
    in {"1", "true", "yes"}
)

fraud_weekly_report_scheduler = None
fund_recommendation_audit_scheduler = None
chat_job_worker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global fraud_weekly_report_scheduler
    global fund_recommendation_audit_scheduler
    global chat_job_worker

    try:
        # Fraud startup initialization
        FraudStartupService.initialize()

        # Initialize and ingest the RAG knowledge base.
        rag_service = RAGService(
            knowledge_base_path="data/knowledge_base",
        )
        rag_service.ingest()

        app.state.rag_service = rag_service
        configure_rag_service(rag_service)

        # Start a shared-Redis chat-job worker in this API instance.
        chat_job_worker = ChatJobWorker(redis_client)
        await chat_job_worker.start()

        # Prewarm queries learned from recent Redis query popularity.
        try:
            warmed_count = await prewarm_rag_cache()
            print(
                f"[RAG CACHE] Prewarmed "
                f"{warmed_count} popular queries"
            )
        except Exception as exc:
            # Cache prewarming is optional; failure must not prevent startup.
            print(f"[RAG CACHE] Prewarming skipped: {exc}")

        # Run scheduled jobs only in instances where the flag is enabled.
        if ENABLE_BACKGROUND_SCHEDULERS:
            fraud_weekly_report_service = (
                FraudWeeklyReportNotificationService()
            )
            fraud_weekly_report_scheduler = (
                FraudWeeklyReportScheduler(
                    report_service=fraud_weekly_report_service,
                )
            )
            fraud_weekly_report_scheduler.start()

            fund_recommendation_audit_service = (
                FundRecommendationAuditReportService()
            )
            fund_recommendation_audit_scheduler = (
                FundRecommendationAuditScheduler(
                    report_service=fund_recommendation_audit_service,
                )
            )
            fund_recommendation_audit_scheduler.start()

        yield

    finally:
        if chat_job_worker is not None:
            await chat_job_worker.stop()
            chat_job_worker = None

        if fraud_weekly_report_scheduler is not None:
            fraud_weekly_report_scheduler.shutdown()
            fraud_weekly_report_scheduler = None

        if fund_recommendation_audit_scheduler is not None:
            fund_recommendation_audit_scheduler.shutdown()
            fund_recommendation_audit_scheduler = None


app = FastAPI(
    title="PaiseWise AI Assistant",
    description="Conversational AI backend for PaiseWise",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "paisewise-ai",
    }


app.include_router(chat_router)
app.include_router(chat_jobs_router)
app.include_router(portfolio_analytics_router)
app.include_router(what_if_router)
app.include_router(portfolio_analytics_history_router)
app.include_router(portfolio_comparison_router)
app.include_router(churn_router)
app.include_router(market_context_router)
app.include_router(stock_news_router)
app.include_router(sector_news_router)
app.include_router(stock_discovery_router)

# Fraud scoring and fraud case management
app.include_router(fraud_router)
app.include_router(fraud_cases_router)

# Mutual-fund hybrid recommendations
app.include_router(fund_recommendation_router)
>>>>>>> srikanth_paise_wise_aiml
