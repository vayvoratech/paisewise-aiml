import os
import joblib

from sklearn.metrics import f1_score


# --------------------------------------------------
# Model paths
# --------------------------------------------------

MODEL_DIR = "../data/churn/models"

CURRENT_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "current_churn_model.pkl"
)


# --------------------------------------------------
# Validate Models
# --------------------------------------------------

def validate_models(training_result):

    # --------------------------------------------------
    # Get new model information
    # --------------------------------------------------

    new_model = training_result["model"]

    X_holdout = training_result["X_holdout"]

    y_holdout = training_result["y_holdout"]

    # --------------------------------------------------
    # Predict using new model
    # --------------------------------------------------

    new_predictions = new_model.predict(
        X_holdout
    )

    new_f1 = f1_score(
        y_holdout,
        new_predictions,
        zero_division=0
    )

    # --------------------------------------------------
    # Check whether current model exists
    # --------------------------------------------------

    if not os.path.exists(
        CURRENT_MODEL_PATH
    ):

        print("\nNo current model found.")

        print(
            "New model will become the current model."
        )

        return {
            "current_f1": 0,
            "new_f1": new_f1,
            "improvement": 1.0,
            "deploy": True
        }

    # --------------------------------------------------
    # Load current model
    # --------------------------------------------------

    current_model = joblib.load(
        CURRENT_MODEL_PATH
    )

    # --------------------------------------------------
    # Predict using current model
    # --------------------------------------------------

    current_predictions = current_model.predict(
        X_holdout
    )

    current_f1 = f1_score(
        y_holdout,
        current_predictions,
        zero_division=0
    )

    # --------------------------------------------------
    # Calculate improvement
    # --------------------------------------------------

    if current_f1 == 0:

        improvement = 1.0

    else:

        improvement = (
            (new_f1 - current_f1)
            / current_f1
        )

    # --------------------------------------------------
    # Display validation result
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("CHURN MODEL VALIDATION")
    print("=" * 60)

    print(
        f"Current F1 : {current_f1:.2%}"
    )

    print(
        f"New F1     : {new_f1:.2%}"
    )

    print(
        f"Improvement: {improvement:.2%}"
    )

    # --------------------------------------------------
    # Deployment decision
    # --------------------------------------------------

    if new_f1 > current_f1:

        print("\nNew model is better.")

        deploy = True

    else:

        print(
            "\nCurrent model is better or equal."
        )

        deploy = False

    return {
        "current_f1": current_f1,
        "new_f1": new_f1,
        "improvement": improvement,
        "deploy": deploy
    }