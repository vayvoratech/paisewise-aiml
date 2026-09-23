import os
import joblib

from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from xgboost import XGBClassifier

from churn_data import load_churn_data


# ============================================================
# MODEL PATH
# ============================================================

MODEL_DIR = "../data/churn/models"

NEW_MODEL_PATH = os.path.join(

    MODEL_DIR,

    "new_churn_model.pkl"

)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [

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


# ============================================================
# TARGET
# ============================================================

TARGET = "churned"


# ============================================================
# TRAIN MODEL
# ============================================================

def train_churn_model():

    print("\n" + "=" * 60)

    print(
        "TRAINING NEW CHURN MODEL"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    data = load_churn_data()

    # --------------------------------------------------------
    # Check required columns
    # --------------------------------------------------------

    required_columns = FEATURES + [TARGET]

    missing_columns = [

        column

        for column in required_columns

        if column not in data.columns

    ]

    if missing_columns:

        raise ValueError(

            f"Missing columns: {missing_columns}"

        )

    # --------------------------------------------------------
    # X and y
    # --------------------------------------------------------

    X = data[FEATURES]

    y = data[TARGET]

    print(
        "\nTotal records:",
        len(data)
    )

    print(
        "Number of features:",
        len(FEATURES)
    )

    # --------------------------------------------------------
    # Check target classes
    # --------------------------------------------------------

    if y.nunique() < 2:

        raise ValueError(

            "Dataset must contain both "
            "churned=0 and churned=1."

        )

    # ========================================================
    # TRAIN / HOLDOUT SPLIT
    # ========================================================

    X_train, X_holdout, y_train, y_holdout = (

        train_test_split(

            X,

            y,

            test_size=0.20,

            random_state=42,

            stratify=y

        )

    )

    print(
        "\nTraining records:",
        len(X_train)
    )

    print(
        "Holdout records:",
        len(X_holdout)
    )

    # ========================================================
    # XGBOOST
    # ========================================================

    model = XGBClassifier(

        n_estimators=100,

        max_depth=4,

        learning_rate=0.1,

        random_state=42,

        eval_metric="logloss"

    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    print(
        "\nTraining XGBoost..."
    )

    model.fit(

        X_train,

        y_train

    )

    print(
        "Training completed."
    )

    # ========================================================
    # HOLDOUT PREDICTION
    # ========================================================

    predictions = model.predict(

        X_holdout

    )

    # ========================================================
    # METRICS
    # ========================================================

    accuracy = accuracy_score(

        y_holdout,

        predictions

    )

    precision = precision_score(

        y_holdout,

        predictions,

        zero_division=0

    )

    recall = recall_score(

        y_holdout,

        predictions,

        zero_division=0

    )

    f1 = f1_score(

        y_holdout,

        predictions,

        zero_division=0

    )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print("\n" + "=" * 60)

    print(
        "NEW CHURN MODEL PERFORMANCE"
    )

    print("=" * 60)

    print(
        f"Accuracy : {accuracy:.2%}"
    )

    print(
        f"Precision: {precision:.2%}"
    )

    print(
        f"Recall   : {recall:.2%}"
    )

    print(
        f"F1 Score : {f1:.2%}"
    )

    # ========================================================
    # SAVE MODEL
    # ========================================================

    os.makedirs(

        MODEL_DIR,

        exist_ok=True

    )

    joblib.dump(

        model,

        NEW_MODEL_PATH

    )

    print(
        "\nNew model saved:"
    )

    print(
        NEW_MODEL_PATH
    )

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "model": model,

        "accuracy": accuracy,

        "precision": precision,

        "recall": recall,

        "f1": f1,

        "X_holdout": X_holdout,

        "y_holdout": y_holdout

    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    result = train_churn_model()

    print(
        "\nTraining completed successfully."
    )