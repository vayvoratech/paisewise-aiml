from fastapi import APIRouter
from pydantic import BaseModel
from services.jargon_service import get_jargon
from utils.rate_limiter import check_rate_limit

router = APIRouter()


class JargonRequest(BaseModel):
    term: str
    language: str = "en"


@router.post("/ai/jargon")
async def explain_jargon(request: JargonRequest):
# Temporary identifier.
# Replace with authenticated userId when available.
    user_id = request.term.lower()

    allowed = check_rate_limit(user_id)

    if not allowed:
        return {
            "message": "Rate limit exceeded. Please try again later."
        }


    result = get_jargon(
        request.term,
        request.language
    )

    return result