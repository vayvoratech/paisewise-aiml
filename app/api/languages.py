from fastapi import APIRouter

from app.services.language_service import get_languages

router = APIRouter()


@router.get("/ai/languages")
def supported_languages():
    
    """Return the 22 Indian scheduled languages supported by the AI layer."""
    return {"languages": get_languages()}
