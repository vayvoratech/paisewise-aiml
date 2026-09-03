import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score


# 1. Load data
df = pd.read_csv("../data/churn/user_activity.csv")

print("Data loaded successfully!")
print("Total users:", len(df))


# 2. Create Day-7 features
df["d7_lesson_count"] = df["lessons_completed"]
df["d7_quiz_count"] = df["quizzes_completed"]
df["d7_paper_trade_count"] = df["paper_trades"]
df["d7_streak_days"] = df["streak_days"]
df["d7_xp_earned"] = df["xp_earned"]

df["d7_notification_open_rate"] = (
    df["notifications_opened"] /
    df["notifications_received"].replace(0, 1)
)

df["onboarding_goal_set"] = df["goal_set"].astype(int)
df["kyc_completed_d7"] = df["kyc_completed"].astype(int)
df["first_paper_trade_d7"] = df["first_paper_trade"].astype(int)


# 3. Convert churn status into 0 and 1
df["churn"] = (
    df["churn_status"] == "Churned"
).astype(int)


# 4. Show churn distribution
print("\nChurn Distribution")
print(df["churn_status"].value_counts())

print("\nChurned users:", df["churn"].sum())
print("Retained users:", len(df) - df["churn"].sum())


# 5. Select features
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

X = df[features]
y = df["churn"]


# 6. Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nData Split")
print("Training users:", len(X_train))
print("Testing users:", len(X_test))


# 7. Create and train XGBoost model
model = XGBClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    random_state=42,
    eval_metric="logloss"
)

print("\nTraining XGBoost model...")
model.fit(X_train, y_train)

print("Model training completed!")


# 8. Predict churn probability
probabilities = model.predict_proba(X_test)[:, 1]


# 9. Calculate AUC-ROC
auc = roc_auc_score(
    y_test,
    probabilities
)

print("\nModel Evaluation")
print("AUC-ROC:", round(auc, 3))


# 10. Create results table
results = pd.DataFrame({
    "actual_churn": y_test.values,
    "churn_probability": probabilities
})


# 11. Get top 20% high-risk users
results = results.sort_values(
    "churn_probability",
    ascending=False
)

top_20_count = max(
    1,
    int(len(results) * 0.20)
)

top_20 = results.head(top_20_count)


# 12. Calculate Precision @ Top 20%
precision_top_20 = top_20["actual_churn"].mean()

print(
    "Precision @ Top 20%:",
    round(precision_top_20, 3)
)

print("High-risk users:", len(top_20))

print(
    "Actually churned:",
    int(top_20["actual_churn"].sum())
)


# 13. Show high-risk users
print("\nTop High-Risk Users")
print(top_20)