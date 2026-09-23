# ============================================================
# PAISEWISE PERSONALISATION
# NOTIFICATION TIMING OPTIMISER
# ============================================================

from collections import Counter

from .learning_dna import get_user_learning_data


# ------------------------------------------------------------
# Find optimal engagement hour
# ------------------------------------------------------------

def find_optimal_engagement_hour(user_id: str):

    user_data = get_user_learning_data(user_id)

    if not user_data:
        return None

    activity_hours = user_data.get(
        "activity_hours",
        []
    )

    if not activity_hours:
        return None

    hour_counts = Counter(activity_hours)

    optimal_hour = hour_counts.most_common(1)[0][0]

    return optimal_hour


# ------------------------------------------------------------
# Format notification time
# ------------------------------------------------------------

def format_notification_time(hour: int):

    return f"{hour:02d}:00"


# ------------------------------------------------------------
# Build notification schedule
# ------------------------------------------------------------

def build_notification_schedule(user_id: str):

    user_data = get_user_learning_data(user_id)

    if not user_data:
        return None

    activity_hours = user_data.get(
        "activity_hours",
        []
    )

    if not activity_hours:
        return {
            "user_id": user_id,
            "optimal_time": None,
            "reason": "Not enough activity data."
        }

    hour_counts = Counter(activity_hours)

    optimal_hour = hour_counts.most_common(1)[0][0]

    optimal_time = format_notification_time(
        optimal_hour
    )

    return {
        "user_id": user_id,
        "optimal_time": optimal_time,
        "optimal_hour": optimal_hour,
        "activity_distribution": dict(
            sorted(hour_counts.items())
        ),
        "reason": (
            "Notification time is based on the user's "
            "historical learning activity."
        )
    }