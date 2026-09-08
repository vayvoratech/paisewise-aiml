import joblib
import pandas as pd

MODEL_PATH = "../data/churn/models/new_churn_model.pkl"

model = joblib.load(MODEL_PATH)

features = [
    "d7_lesson_count",
    "d7_quiz_count",
    "d7_paper_trade_count",
    "d7_streak_days",
    "d7_xp_earned",
    "d7_notification_open_rate",
    "onboarding_goal_set",
    "kyc_completed_d7",
    "first_paper_trade_d7"
]


# Very active user
low_risk = pd.DataFrame([{
    "d7_lesson_count": 20,
    "d7_quiz_count": 15,
    "d7_paper_trade_count": 10,
    "d7_streak_days": 7,
    "d7_xp_earned": 500,
    "d7_notification_open_rate": 0.95,
    "onboarding_goal_set": 1,
    "kyc_completed_d7": 1,
    "first_paper_trade_d7": 1
}])


# Very inactive user
high_risk = pd.DataFrame([{
    "d7_lesson_count": 0,
    "d7_quiz_count": 0,
    "d7_paper_trade_count": 0,
    "d7_streak_days": 0,
    "d7_xp_earned": 0,
    "d7_notification_open_rate": 0.0,
    "onboarding_goal_set": 0,
    "kyc_completed_d7": 0,
    "first_paper_trade_d7": 0
}])


print("LOW RISK USER")
print(model.predict_proba(low_risk))

print("\nHIGH RISK USER")
print(model.predict_proba(high_risk))