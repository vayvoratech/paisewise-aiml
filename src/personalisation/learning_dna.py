# ============================================================
# PAISEWISE PERSONALISATION - LEARNING DNA
# ============================================================

from collections import Counter
from datetime import datetime


# ------------------------------------------------------------
# Sample user learning data
# ------------------------------------------------------------
# This is development/sample data for Task 5.
# Later, this can be replaced with real user activity from DB.
# ------------------------------------------------------------

USER_LEARNING_DATA = {
    "U001": {
        "topics": [
            "mutual_funds",
            "sip",
            "mutual_funds",
            "diversification",
            "sip"
        ],
        "completed_lessons": 12,
        "completed_quizzes": 8,
        "current_streak": 5,
        "preferred_difficulty": "beginner",
        "activity_hours": [19, 20, 20, 20, 21, 19],
        "last_active": "2026-09-16T20:15:00"
    },

    "U002": {
        "topics": [
            "stocks",
            "stocks",
            "risk",
            "portfolio",
            "stocks"
        ],
        "completed_lessons": 8,
        "completed_quizzes": 4,
        "current_streak": 2,
        "preferred_difficulty": "intermediate",
        "activity_hours": [10, 11, 10, 12, 11],
        "last_active": "2026-09-16T11:20:00"
    },

    "U003": {
        "topics": [
            "saving",
            "budgeting",
            "emergency_fund",
            "saving",
            "budgeting"
        ],
        "completed_lessons": 15,
        "completed_quizzes": 10,
        "current_streak": 10,
        "preferred_difficulty": "beginner",
        "activity_hours": [7, 8, 8, 9, 8, 7],
        "last_active": "2026-09-16T08:30:00"
    }
}


# ------------------------------------------------------------
# Get user learning data
# ------------------------------------------------------------

def get_user_learning_data(user_id: str):
    return USER_LEARNING_DATA.get(user_id)


# ------------------------------------------------------------
# Find user's most interested topic
# ------------------------------------------------------------

def get_top_topic(topics: list):
    if not topics:
        return None

    topic_counts = Counter(topics)

    return topic_counts.most_common(1)[0][0]


# ------------------------------------------------------------
# Find user's preferred engagement hour
# ------------------------------------------------------------

def get_preferred_hour(activity_hours: list):
    if not activity_hours:
        return None

    hour_counts = Counter(activity_hours)

    return hour_counts.most_common(1)[0][0]


# ------------------------------------------------------------
# Build Learning DNA
# ------------------------------------------------------------

def build_learning_dna(user_id: str):

    user_data = get_user_learning_data(user_id)

    if not user_data:
        return None

    top_topic = get_top_topic(
        user_data.get("topics", [])
    )

    preferred_hour = get_preferred_hour(
        user_data.get("activity_hours", [])
    )

    return {
        "user_id": user_id,

        "interests": {
            "topics": user_data.get("topics", []),
            "top_topic": top_topic
        },

        "learning_activity": {
            "completed_lessons": user_data.get(
                "completed_lessons", 0
            ),
            "completed_quizzes": user_data.get(
                "completed_quizzes", 0
            ),
            "current_streak": user_data.get(
                "current_streak", 0
            )
        },

        "learning_preference": {
            "difficulty": user_data.get(
                "preferred_difficulty",
                "beginner"
            )
        },

        "engagement": {
            "preferred_hour": preferred_hour,
            "last_active": user_data.get(
                "last_active"
            )
        }
    }