from fastapi import APIRouter

from app.services.language_service import get_languages

router = APIRouter()


@router.get("/ai/languages")
def supported_languages():
    
    """Returns the 22 Indian scheduled languages...."""
    return {"languages": get_languages()}
