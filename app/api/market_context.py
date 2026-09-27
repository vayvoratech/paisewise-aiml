from fastapi import APIRouter, HTTPException
from app.services.market_context import build_market_context
from app.services.news_service import get_news
from app.services.news_context_service import NewsContextService

router = APIRouter(prefix="/ai", tags=["Market Context"])
news_context = NewsContextService()

@router.get("/market-context")
def market_context():
    try:
        articles = news_context.enrich(get_news(20))
        return {
            "news": articles,
            "sector_sentiment": news_context.sector_digest(articles),
            "context": build_market_context([], [], articles),
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.get("/stock-news/{symbol}")
def stock_news(symbol: str):
    try:
        articles = news_context.enrich(get_news(20))
        matches = [a for a in articles if symbol.lower() in f"{a.get('title','')} {a.get('description','')}".lower()]
        return {"symbol": symbol, "items": matches[:3]}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.get("/sector-news/{sector}")
def sector_news(sector: str):
    try:
        articles = news_context.enrich(get_news(20))
        matches = [a for a in articles if a.get("sector", "").lower() == sector.lower()]
        return {"sector": sector, "items": matches, "digest": news_context.sector_digest(matches)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
