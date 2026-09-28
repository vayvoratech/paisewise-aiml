from fastapi import APIRouter, HTTPException

from app.services.market_context import build_market_context
from app.services.news_service import get_news
from app.services.news_context_service import NewsContextService


router = APIRouter(
    prefix="/ai",
    tags=["Market Context"],
)


# NewsContextService loads the BART model.
# Keep it lazy so the model is not loaded while
# FastAPI is importing the application.

news_context = None


def get_news_context() -> NewsContextService:
    global news_context

    if news_context is None:
        news_context = NewsContextService()

    return news_context


@router.get("/market-context")
def market_context():
    try:
        service = get_news_context()
        articles = service.enrich(get_news(20))

        return {
            "news": articles,
            "sector_sentiment": service.sector_digest(articles),
            "context": build_market_context([], [], articles),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.get("/stock-news/{symbol}")
def stock_news(symbol: str):
    try:
        service = get_news_context()
        articles = service.enrich(get_news(20))

        matches = [
            article
            for article in articles
            if symbol.lower()
            in f"{article.get('title', '')} {article.get('description', '')}".lower()
        ]

        return {
            "symbol": symbol,
            "items": matches[:3],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.get("/sector-news/{sector}")
def sector_news(sector: str):
    try:
        service = get_news_context()
        articles = service.enrich(get_news(20))

        matches = [
            article
            for article in articles
            if article.get("sector", "").lower() == sector.lower()
        ]

        return {
            "sector": sector,
            "items": matches,
            "digest": service.sector_digest(matches),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
