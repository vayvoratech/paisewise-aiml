from fastapi import APIRouter, HTTPException
from app.services.lesson_ab import assign_lesson_variant, cache_lesson_recommendations, get_cached_lesson_recommendations
from app.services.lesson_personalization import classify_lesson_difficulty, generate_learning_path, build_user_learning_profile

router = APIRouter()


def _load_learning_data(user_id):
    from database.database import get_db_connection
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT lesson_name, completed FROM lesson_progress WHERE user_id = %s", (user_id,))
            lessons = [{"lesson_name": r[0], "completed": r[1]} for r in cursor.fetchall()]
            cursor.execute("SELECT quiz_name, score FROM quiz_attempts WHERE user_id = %s", (user_id,))
            quizzes = [{"quiz_name": r[0], "score": r[1]} for r in cursor.fetchall()]
            return lessons, quizzes
    finally:
        connection.close()


@router.post("/ai/next-lessons")
def next_lessons(payload: dict):
    user_id = str(payload.get("userId", "")).strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="userId is required")
    cached = get_cached_lesson_recommendations(user_id)
    if cached:
        return {**cached, "source": "cache"}
    try:
        lessons, quizzes = _load_learning_data(user_id)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unable to load learning profile: {error}")
    completed = [x["lesson_name"] for x in lessons if x.get("completed")]
    scores = {}
    for item in quizzes:
        scores.setdefault(item["quiz_name"], []).append(item["score"])
    scores = {k: sum(v) / len(v) for k, v in scores.items()}
    path = generate_learning_path(completed, scores, 3)
    result = {"userId": user_id, "variant": assign_lesson_variant(user_id), "nextLessons": path}
    cache_lesson_recommendations(user_id, result)
    return result


@router.get("/ai/lesson-difficulty/{lessonId}/{userId}")
def lesson_difficulty(lessonId: str, userId: str):
    try:
        _, quizzes = _load_learning_data(userId)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unable to load quiz data: {error}")
    scores = [q["score"] for q in quizzes if q["quiz_name"] == lessonId]
    score = sum(scores) / len(scores) if scores else 50
    return {"lessonId": lessonId, "userId": userId, "difficulty": classify_lesson_difficulty(score), "scoreBasis": round(score, 2)}
