from app.pipelines.validate_features import validate_feature_ranges
from app.utils.data_validation import validate_age, validate_income, validate_risk_profile
import pandas as pd


def test_feature_range_validation():
    errors = validate_feature_ranges({
        "lesson_completion_rate": 0.5,
        "quiz_avg_score": 80,
        "streak_days": 2,
        "total_xp": 100,
        "paper_trade_count": 3,
        "paper_trade_profit_rate": 0.4,
        "session_duration": 20,
        "screens_visited": 5,
        "lessons_started": 2,
        "quizzes_taken": 1,
    })
    assert errors == []


def test_user_validation_helpers():
    df = pd.DataFrame({
        "age": [25, 110],
        "annual_income": [100000, -1],
        "risk_profile": ["Moderate", "Unknown"],
    })

    assert len(validate_age(df)) == 1
    assert len(validate_income(df)) == 1
    assert len(validate_risk_profile(df)) == 1
