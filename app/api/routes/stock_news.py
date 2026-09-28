from fastapi import APIRouter, HTTPException

from app.schemas.stock_news import (
    StockNewsItem,
    StockNewsResponse,
)
from app.services.news_cache_service import NewsCacheService
from app.services.stock_news_service import StockNewsService


router = APIRouter(
    prefix="/ai",
    tags=["Stock News"],
)


@router.get(
    "/stock-news/{symbol}",
    response_model=StockNewsResponse,
)
async def get_stock_news(
    symbol: str,
) -> StockNewsResponse:

    if not symbol or not symbol.strip():
        raise HTTPException(
            status_code=400,
            detail="symbol cannot be empty",
        )

    normalized_symbol = symbol.strip().upper()

    cache_key = f"stock-news:{normalized_symbol}"

    service = StockNewsService()

    # -------------------------------------------------
    # Check the existing processed cache.
    # -------------------------------------------------
    cached = NewsCacheService.get_news_cache(
        cache_key
    )

    # -------------------------------------------------
    # If a cache exists, perform only a lightweight
    # source freshness check.
    #
    # This does NOT run LLM sentiment processing.
    # -------------------------------------------------
    if cached is not None:
        try:
            (
                latest_article_key,
                latest_published_at,
            ) = service.get_latest_article_metadata(
                normalized_symbol
            )

            # No newer article is available.
            # Return the already processed result.
            if not NewsCacheService.is_newer_article_available(
                cached=cached,
                latest_article_key=latest_article_key,
                latest_published_at=latest_published_at,
            ):
                cached_articles = cached.get(
                    "articles",
                    [],
                )

                return StockNewsResponse.model_validate(
                    cached_articles
                )

        except RuntimeError:
            # If freshness checking fails, retain the
            # existing cached result rather than
            # unnecessarily re-processing the news.
            cached_articles = cached.get(
                "articles",
                [],
            )

            if cached_articles:
                return StockNewsResponse.model_validate(
                    cached_articles
                )

    try:
        # -------------------------------------------------
        # No cache or a new article is available.
        #
        # Only now do we run the complete news pipeline,
        # including sentiment processing.
        # -------------------------------------------------
        articles = await service.get_news(
            symbol=normalized_symbol,
            limit=3,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve stock news.",
        ) from exc

    news = [
        StockNewsItem(
            title=article.title,
            summary=article.summary,
            source=article.source,
            publishedAt=article.published_at,
            url=article.url,
            sentiment=article.sentiment or "neutral",
        )
        for article in articles
    ]

    response = StockNewsResponse(
        symbol=normalized_symbol,
        news=news,
    )

    # -------------------------------------------------
    # Store the processed result together with the
    # latest source article metadata.
    #
    # NewsCacheService keeps this entry for 2 hours.
    # -------------------------------------------------
    latest_article_key = None
    latest_published_at = None

    if articles:
        latest_article = max(
            articles,
            key=lambda article: service._publication_timestamp(
                article.published_at
            ),
        )

        latest_article_key = (
            latest_article.url
            or latest_article.title
        )

        latest_published_at = (
            latest_article.published_at
        )

    NewsCacheService.set_news_cache(
        cache_key=cache_key,
        articles=response.model_dump(),
        latest_article_key=latest_article_key,
        latest_published_at=latest_published_at,
    )

    return response