
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.jargon_service import get_jargon
from utils.rate_limiter import check_rate_limit


router = APIRouter()


class JargonRequest(BaseModel):
    term: str
    language: str = "en"
    userId: str | None = None


class JargonResponse(BaseModel):
    term: str
    language: str
    explanation: str


@router.post(
    "/ai/jargon",
    response_model=JargonResponse
)
async def explain_jargon(request: JargonRequest):

    # Spring Boot should send userId; X-User-Id is also accepted for internal calls.
    user_id = request.userId or "anonymous"

    allowed = check_rate_limit(user_id)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

    result = get_jargon(
        request.term,
        request.language
    )

    return result

