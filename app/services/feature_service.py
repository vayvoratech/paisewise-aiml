from database.database import get_db_connection

FEATURE_COLUMNS = [
    "age", "annual_income", "monthly_investment", "portfolio_value",
    "risk_profile", "investment_experience_years", "sip_count", "kyc_completed",
    "lesson_completion_rate", "quiz_avg_score", "streak_days", "total_xp",
    "preferred_language", "onboarding_goal", "age_proxy", "city_tier",
    "paper_trade_count", "paper_trade_profit_rate", "time_of_day",
    "session_duration", "screens_visited", "lessons_started", "quizzes_taken",
]


def get_latest_features(user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {', '.join(FEATURE_COLUMNS)}, feature_version, updated_at
                FROM user_features
                WHERE user_id = %s
                LIMIT 1
                """,
                (user_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        values = dict(zip(FEATURE_COLUMNS, row[:len(FEATURE_COLUMNS)]))
        version = row[len(FEATURE_COLUMNS)]
        updated_at = row[len(FEATURE_COLUMNS) + 1]
        return {
            "user_id": str(user_id),
            "features": {k: (float(v) if hasattr(v, "as_tuple") else v) for k, v in values.items()},
            "feature_version": version or "v1",
            "updated_at": updated_at.isoformat() if updated_at else None,
        }
    finally:
        connection.close()
