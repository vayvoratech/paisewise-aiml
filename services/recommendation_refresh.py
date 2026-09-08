from services.recommendation_cache import invalidate_recommendation_cache


def refresh_recommendation_for_lesson_completion(user_id):      
    invalidate_recommendation_cache(user_id)


def refresh_recommendation_for_goal_update(user_id):
    invalidate_recommendation_cache(user_id)