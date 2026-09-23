# ============================================================
# PAISEWISE PERSONALISATION ENGINE
# ============================================================

from .learning_dna import build_learning_dna
from .notification_optimizer import build_notification_schedule
from .streak_recovery import generate_streak_recovery
from .lesson_recommender import recommend_daily_lesson


def build_content_order(learning_dna: dict):

    interests = learning_dna.get("interests", {})
    activity = learning_dna.get("learning_activity", {})
    preference = learning_dna.get("learning_preference", {})

    top_topic = interests.get("top_topic")
    completed_quizzes = activity.get("completed_quizzes", 0)
    current_streak = activity.get("current_streak", 0)
    difficulty = preference.get("difficulty", "beginner")

    content = []

    content.append({
        "content_type": "daily_lesson",
        "priority": 1,
        "reason": "Daily learning content is recommended."
    })

    if top_topic:
        content.append({
            "content_type": "continue_learning",
            "topic": top_topic,
            "priority": 2,
            "reason": (
                f"Recommended because {top_topic} "
                "is the user's main learning interest."
            )
        })
    else:
        content.append({
            "content_type": "continue_learning",
            "priority": 2,
            "reason": "Continue the user's previous learning."
        })

    content.append({
        "content_type": "quiz",
        "priority": 3,
        "difficulty": difficulty,
        "priority_reason": (
            "User has previous quiz activity."
            if completed_quizzes > 0
            else
            "Quiz is recommended to build learning activity."
        )
    })

    content.append({
        "content_type": "recommended_topic",
        "topic": top_topic or "personal_finance",
        "priority": 4,
        "reason": (
            f"Based on the user's frequent interest "
            f"in {top_topic}."
            if top_topic
            else
            "Default financial education topic."
        )
    })

    content.append({
        "content_type": "streak",
        "current_streak": current_streak,
        "priority": 5,
        "reason": (
            "User has an active learning streak."
            if current_streak > 0
            else
            "Streak recovery content can be shown."
        )
    })

    return content


def personalise_user(user_id: str):

    learning_dna = build_learning_dna(user_id)

    if not learning_dna:
        return None

    content_order = build_content_order(learning_dna)

    return {
        "user_id": user_id,
        "personalisation": {
            "top_topic": learning_dna["interests"]["top_topic"],
            "difficulty": learning_dna[
                "learning_preference"
            ]["difficulty"],
            "current_streak": learning_dna[
                "learning_activity"
            ]["current_streak"],
            "preferred_hour": learning_dna[
                "engagement"
            ]["preferred_hour"]
        },
        "content_order": content_order
    }


# ============================================================
# SINGLE MOBILE PERSONALISATION API DATA
# ============================================================

def build_personalised_home(user_id: str):

    learning_dna = build_learning_dna(user_id)

    if not learning_dna:
        return None

    home_screen = personalise_user(user_id)

    daily_lesson = recommend_daily_lesson(user_id)

    notification = build_notification_schedule(user_id)

    streak_recovery = generate_streak_recovery(user_id)

    return {
        "user_id": user_id,

        "learning_dna": learning_dna,

        "home_screen": home_screen,

        "daily_lesson": daily_lesson,

        "notification": notification,

        "streak_recovery": streak_recovery
    }