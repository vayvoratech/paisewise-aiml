from fastapi import APIRouter, HTTPException

from app.schemas.portfolio_analytics import (
    PortfolioAnalyticsResponse,
)
from app.services.portfolio_analytics_service import (
    PortfolioAnalyticsService,
)
from app.services.portfolio_health_service import (
    PortfolioHealthService,
)
from app.services.llm.gemini_provider import (
    GeminiProvider,
)


router = APIRouter(
    prefix="/ai",
    tags=["Portfolio Analytics"],
)


@router.get(
    "/portfolio-analytics/{userId}",
    response_model=PortfolioAnalyticsResponse,
)
async def get_portfolio_analytics(
    userId: str,
) -> PortfolioAnalyticsResponse:

    try:
        # ------------------------------------------
        # 1. Calculate numeric portfolio analytics
        # ------------------------------------------

        analytics_service = (
            PortfolioAnalyticsService()
        )

        analytics = analytics_service.calculate(
            user_id=userId
        )

        # ------------------------------------------
        # 2. Convert analytics to dictionary
        # ------------------------------------------

        analytics_data = (
            analytics.model_dump()
        )

        # ------------------------------------------
        # 3. Generate LLM health report
        # ------------------------------------------

        llm_provider = GeminiProvider()

        health_service = (
            PortfolioHealthService(
                llm_provider=llm_provider
            )
        )

        health_report = (
            await health_service.generate_report(
                analytics_data
            )
        )

        # ------------------------------------------
        # 4. Return analytics + health report
        # ------------------------------------------

        analytics.healthReport = health_report

        return analytics

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
            detail=(
                "Unable to generate "
                "portfolio analytics."
            ),
        ) from exc