from fastapi import APIRouter, HTTPException
from cache.redis_cache import RedisCache
from services.stock_discovery import discover_stocks

router = APIRouter()
cache = RedisCache()
CACHE_TTL = 6 * 60 * 60


def _get_completed_lessons(user_id):
    try:
        from database.database import get_db_connection
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT lesson_name FROM lesson_progress
                    WHERE user_id = %s AND completed = TRUE
                """, (user_id,))
                return [row[0] for row in cursor.fetchall()]
        finally:
            connection.close()
    except Exception:
        return []


@router.get("/ai/stock-discovery/{userId}")
def stock_discovery(userId: str, riskProfile: str = "moderate", learningLevel: int = 5):
    if learningLevel < 5:
        raise HTTPException(status_code=400, detail="Stock discovery starts at learning Level 5. Complete more learning content first.")
    cache_key = f"stock_discovery:{userId}"
    try:
        cached = cache.get(cache_key)
        if cached:
            return cached
    except Exception:
        pass
    completed_lessons = _get_completed_lessons(userId)
    result = discover_stocks(userId, riskProfile, learningLevel, completed_lessons)
    try:
        cache.set(cache_key, result, expiry=CACHE_TTL)
    except Exception:
        pass
    return result
