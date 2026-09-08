from fastapi import FastAPI

from app.api.routes.chat import (
    router as chat_router,
)
from app.api.routes.portfolio_analytics import (
    router as portfolio_analytics_router,
)
from app.api.routes.what_if import (
    router as what_if_router,
)
from app.api.routes.portfolio_analytics_history import (
    router as portfolio_analytics_history_router,
)
from app.api.routes.portfolio_comparison import (
    router as portfolio_comparison_router,
)
from app.api.routes.churn import (
    router as churn_router,
)


app = FastAPI(
    title="PaiseWise AI Assistant",
    description="Conversational AI backend for PaiseWise",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "paisewise-ai",
    }


# Task 3 - Chat API
app.include_router(
    chat_router
)


# Task 4 - Portfolio Analytics API
app.include_router(
    portfolio_analytics_router
)


# Task 4 - What-If Analyzer API
app.include_router(
    what_if_router
)


# Task 4 - Portfolio Analytics History API
app.include_router(
    portfolio_analytics_history_router
)


# Task 4 - Portfolio Comparison API
app.include_router(
    portfolio_comparison_router
)


# Task 5 - Churn Risk API
app.include_router(
    churn_router
)