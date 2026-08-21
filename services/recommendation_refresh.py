from services.recommendation_cache import invalidate_recommendation_cache


def refresh_recommendation_for_lesson_completion(user_id):
    """
    Invalidate recommendation cache when a user completes a lesson.
    Fresh recommendations will be calculated on the next request.
    """
    invalidate_recommendation_cache(user_id)


def refresh_recommendation_for_goal_update(user_id):
    """
    Invalidate recommendation cache when a user updates their goal.
    Fresh recommendations will be calculated on the next request.
    """
    invalidate_recommendation_cache(user_id)