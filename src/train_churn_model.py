import pandas as pd
import mlflow
import mlflow.xgboost

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# --------------------------------------------------
# Load user activity data
# --------------------------------------------------

df = pd.read_csv("../data/churn/user_activity.csv")


# --------------------------------------------------
# Create Day-7 features
# --------------------------------------------------

df["d7_lesson_count"] = df["lessons_completed"]
df["d7_quiz_count"] = df["quizzes_completed"]
df["d7_paper_trade_count"] = df["paper_trades"]
df["d7_streak_days"] = df["streak_days"]
df["d7_xp_earned"] = df["xp_earned"]

df["d7_notification_open_rate"] = (
    df["notifications_opened"]
    / df["notifications_received"]
)

df["onboarding_goal_set"] = df["goal_set"].astype(int)
df["kyc_completed_d7"] = df["kyc_completed"].astype(int)
df["first_paper_trade_d7"] = df["first_paper_trade"].astype(int)


# --------------------------------------------------
# Create churn target
# --------------------------------------------------

df["churn"] = (
    df["churn_status"] == "Churned"
).astype(int)


# --------------------------------------------------
# Features
# --------------------------------------------------

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


# --------------------------------------------------
# Train / Holdout split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# Create XGBoost model
# --------------------------------------------------

model = XGBClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    random_state=42,
    eval_metric="logloss"
)


# --------------------------------------------------
# Start MLflow experiment
# --------------------------------------------------

mlflow.set_experiment("PaiseWise_Churn_Model")


with mlflow.start_run():

    # Train model
    model.fit(X_train, y_train)

    # --------------------------------------------------
    # Validate on holdout data
    # --------------------------------------------------

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )


    # --------------------------------------------------
    # Log parameters
    # --------------------------------------------------

    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 3)
    mlflow.log_param("learning_rate", 0.1)
    mlflow.log_param("test_size", 0.20)


    # --------------------------------------------------
    # Log validation metrics
    # --------------------------------------------------

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)


    # --------------------------------------------------
    # Save model to MLflow
    # --------------------------------------------------

    mlflow.xgboost.log_model(
        model,
        name="churn_model"
    )


    # --------------------------------------------------
    # Display results
    # --------------------------------------------------

    print("\nChurn Model Validation Results")
    print("-" * 40)

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")

    print("\nMLflow run completed successfully.")