from fastapi import APIRouter, HTTPException

from app.schemas.what_if import (
    WhatIfRequest,
    WhatIfResponse,
)
from app.services.what_if_service import (
    WhatIfService,
)


router = APIRouter(
    prefix="/ai",
    tags=["What-If Analyzer"],
)


@router.post(
    "/portfolio-analytics/what-if",
    response_model=WhatIfResponse,
)
async def calculate_what_if(
    request: WhatIfRequest,
) -> WhatIfResponse:
    """
    Calculate a hypothetical portfolio scenario
    using proportional allocation of an additional
    monthly SIP across the user's existing holdings.
    """
    try:
        service = WhatIfService()

        return service.calculate(request)

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
            detail="Unable to calculate what-if scenario.",
        ) from exc