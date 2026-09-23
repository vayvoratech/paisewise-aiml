# ============================================================
# SMART STREAK RECOVERY
# ============================================================

from .learning_dna import build_learning_dna


# ------------------------------------------------------------
# Generate personalised streak recovery message
# ------------------------------------------------------------

def generate_streak_recovery(user_id: str):

    learning_dna = build_learning_dna(user_id)

    if not learning_dna:
        return None

    activity = learning_dna.get(
        "learning_activity",
        {}
    )

    interests = learning_dna.get(
        "interests",
        {}
    )

    previous_streak = activity.get(
        "current_streak",
        0
    )

    top_topic = interests.get(
        "top_topic"
    )

    completed_lessons = activity.get(
        "completed_lessons",
        0
    )

    # --------------------------------------------------------
    # User still has an active streak
    # --------------------------------------------------------

    if previous_streak > 0:

        return {
            "user_id": user_id,
            "streak_broken": False,
            "current_streak": previous_streak,
            "message": (
                f"You're currently on a {previous_streak}-day "
                "learning streak. Keep it going!"
            ),
            "reason": (
                "The user currently has an active streak, "
                "so recovery is not required."
            )
        }

    # --------------------------------------------------------
    # User has no active streak
    # --------------------------------------------------------

    if top_topic:

        message = (
            f"Your learning journey is waiting for you! "
            f"Come back today and continue learning about "
            f"{top_topic.replace('_', ' ')}."
        )

    else:

        message = (
            "Your learning journey is waiting for you! "
            "Come back today and continue learning."
        )

    return {
        "user_id": user_id,
        "streak_broken": True,
        "current_streak": 0,
        "previous_learning_topic": top_topic,
        "completed_lessons": completed_lessons,
        "message": message,
        "reason": (
            "Message is personalised using the user's "
            "learning history."
        )
    }