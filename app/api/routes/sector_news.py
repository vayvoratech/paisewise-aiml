from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.news_cache_service import NewsCacheService
from app.services.sector_news_service import SectorNewsService


router = APIRouter(
    prefix="/ai",
    tags=["Sector News"],
)


class SectorNewsItem(BaseModel):
    title: str
    summary: str
    source: str
    publishedAt: str
    url: str
    sentiment: str


class SectorNewsResponse(BaseModel):
    sector: str
    news: list[SectorNewsItem] = Field(
        default_factory=list
    )


@router.get(
    "/sector-news/{sector}",
    response_model=SectorNewsResponse,
)
async def get_sector_news(
    sector: str,
) -> SectorNewsResponse:

    if not sector or not sector.strip():
        raise HTTPException(
            status_code=400,
            detail="sector cannot be empty",
        )

    normalized_sector = sector.strip()

    cache_key = (
        f"sector-news:{normalized_sector.lower()}"
    )

    service = SectorNewsService()

    # -------------------------------------------------
    # Check the processed cache first.
    # -------------------------------------------------
    cached = NewsCacheService.get_news_cache(
        cache_key
    )

    # -------------------------------------------------
    # If cached data exists, check whether the source
    # contains a newer article.
    #
    # No LLM processing is performed during this check.
    # -------------------------------------------------
    if cached is not None:
        try:
            (
                latest_article_key,
                latest_published_at,
            ) = service.get_latest_article_metadata(
                normalized_sector
            )

            # No new article:
            # return the already processed result.
            if not NewsCacheService.is_newer_article_available(
                cached=cached,
                latest_article_key=latest_article_key,
                latest_published_at=latest_published_at,
            ):
                cached_response = cached.get(
                    "articles"
                )

                if cached_response:
                    return SectorNewsResponse.model_validate(
                        cached_response
                    )

        except RuntimeError:
            # If freshness checking fails, use the
            # existing processed cache when available.
            cached_response = cached.get(
                "articles"
            )

            if cached_response:
                return SectorNewsResponse.model_validate(
                    cached_response
                )

    try:
        # -------------------------------------------------
        # No cache or new article detected.
        # Run the complete news processing pipeline.
        # -------------------------------------------------
        articles = await service.get_news(
            sector=normalized_sector,
            limit=5,
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
            detail="Unable to retrieve sector news.",
        ) from exc

    news = [
        SectorNewsItem(
            title=article.title,
            summary=article.summary,
            source=article.source,
            publishedAt=article.published_at,
            url=article.url,
            sentiment=article.sentiment or "neutral",
        )
        for article in articles
    ]

    response = SectorNewsResponse(
        sector=normalized_sector,
        news=news,
    )

    # -------------------------------------------------
    # Store processed result + latest article metadata.
    # Redis keeps the entry for 2 hours.
    # -------------------------------------------------
    latest_article_key = None
    latest_published_at = None

    if articles:
        latest_article = max(
            articles,
            key=lambda article: (
                SectorNewsService._publication_timestamp(
                    article.published_at
                )
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