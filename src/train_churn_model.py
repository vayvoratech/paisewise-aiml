import pandas as pd
from xgboost import XGBClassifier


# Load user activity data
df = pd.read_csv("../data/churn/user_activity.csv")


# Create Day-7 features
df["d7_lesson_count"] = df["lessons_completed"]
df["d7_quiz_count"] = df["quizzes_completed"]
df["d7_paper_trade_count"] = df["paper_trades"]
df["d7_streak_days"] = df["streak_days"]
df["d7_xp_earned"] = df["xp_earned"]

df["d7_notification_open_rate"] = (
    df["notifications_opened"]
    / df["notifications_received"]
)


# Rename the boolean fields
df["onboarding_goal_set"] = (
    df["goal_set"].astype(int)
)

df["kyc_completed_d7"] = (
    df["kyc_completed"].astype(int)
)

df["first_paper_trade_d7"] = (
    df["first_paper_trade"].astype(int)
)


# Convert churn status into 0 and 1
df["churn"] = (
    df["churn_status"] == "Churned"
).astype(int)


# Features for the model
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


# Prepare input and target
X = df[features]
y = df["churn"]


# Create XGBoost model
model = XGBClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    random_state=42
)


# Train the model
model.fit(X, y)


# Calculate churn probability
df["churn_probability"] = (
    model.predict_proba(X)[:, 1]
)


# Display results
print("\nChurn Prediction Results")
print("-" * 40)

print(
    df[
        [
            "user_id",
            "churn_status",
            "churn_probability"
        ]
    ]
)