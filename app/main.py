from fastapi import FastAPI

from app.api.fund_recommend import router as fund_recommend_router
from app.api.languages import router as languages_router
from app.api.paper_trade_coach import router as paper_trade_coach_router
from app.api.portfolio_insight import router as portfolio_insight_router

app = FastAPI(
    title="Financial AI Service",
    version="1.1.0",
)

app.include_router(fund_recommend_router)
app.include_router(portfolio_insight_router)
app.include_router(languages_router)
app.include_router(paper_trade_coach_router)
