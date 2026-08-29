import pandas as pd

# Read historical user activity
df = pd.read_csv("../data/churn/user_activity.csv")
# Create churn model features
df["d7_lesson_count"] = df["lessons_completed"]

df["d7_quiz_count"] = df["quizzes_completed"]

df["d7_paper_trade_count"] = df["paper_trades"]

df["d7_streak_days"] = df["streak_days"]

df["d7_xp_earned"] = df["xp_earned"]

df["d7_notification_open_rate"] = (
    df["notifications_opened"]
    / df["notifications_received"]
)

df["onboarding_goal_set"] = df["goal_set"]

df["kyc_completed_d7"] = df["kyc_completed"]

df["first_paper_trade_d7"] = df["first_paper_trade"]

print(df)