def validate_feature_ranges(features):
    checks = {
        "lesson_completion_rate": (0, 1),
        "quiz_avg_score": (0, 100),
        "streak_days": (0, None),
        "total_xp": (0, None),
        "paper_trade_count": (0, None),
        "paper_trade_profit_rate": (0, 1),
        "session_duration": (0, None),
        "screens_visited": (0, None),
        "lessons_started": (0, None),
        "quizzes_taken": (0, None),
    }

    errors = []

    for name, (minimum, maximum) in checks.items():
        value = features.get(name)

        if value is None:
            continue

        if minimum is not None and value < minimum:
            errors.append(f"{name}: below minimum")

        if maximum is not None and value > maximum:
            errors.append(f"{name}: above maximum")

    return errors
