import os
import shutil
import joblib

from sklearn.metrics import f1_score


# ============================================================
# MODEL PATHS
# ============================================================

MODEL_DIR = "../data/churn/models"

CURRENT_MODEL_PATH = os.path.join(

    MODEL_DIR,

    "churn_model.pkl"

)

NEW_MODEL_PATH = os.path.join(

    MODEL_DIR,

    "new_churn_model.pkl"

)


# ============================================================
# DEPLOYMENT FUNCTION
# ============================================================

def deploy_new_model(training_result):

    print("\n" + "=" * 60)

    print(
        "MODEL DEPLOYMENT VALIDATION"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # Get new model
    # --------------------------------------------------------

    new_model = training_result["model"]

    X_holdout = training_result["X_holdout"]

    y_holdout = training_result["y_holdout"]

    # ========================================================
    # NEW MODEL F1
    # ========================================================

    new_predictions = new_model.predict(

        X_holdout

    )

    new_f1 = f1_score(

        y_holdout,

        new_predictions,

        zero_division=0

    )

    # ========================================================
    # CURRENT MODEL F1
    # ========================================================

    if os.path.exists(CURRENT_MODEL_PATH):

        print(
            "\nCurrent model found."
        )

        current_model = joblib.load(

            CURRENT_MODEL_PATH

        )

        current_predictions = current_model.predict(

            X_holdout

        )

        current_f1 = f1_score(

            y_holdout,

            current_predictions,

            zero_division=0

        )

    else:

        print(
            "\nNo current model found."
        )

        print(
            "This is the first model deployment."
        )

        current_f1 = 0.0

    # ========================================================
    # IMPROVEMENT
    # ========================================================

    improvement = new_f1 - current_f1

    print(
        "\nCurrent model F1:",
        f"{current_f1:.2%}"
    )

    print(
        "New model F1:",
        f"{new_f1:.2%}"
    )

    print(
        "Improvement:",
        f"{improvement:.2%}"
    )

    # ========================================================
    # DEPLOYMENT RULE
    # ========================================================
    #
    # Deploy only if improvement > 2%
    # ========================================================

    if improvement > 0.02:

        print(
            "\nImprovement is greater than 2%."
        )

        print(
            "Deploying new model..."
        )

        os.makedirs(

            MODEL_DIR,

            exist_ok=True

        )

        # ----------------------------------------------------
        # Copy new model to current model
        # ----------------------------------------------------

        if os.path.exists(NEW_MODEL_PATH):

            shutil.copy2(

                NEW_MODEL_PATH,

                CURRENT_MODEL_PATH

            )

        else:

            joblib.dump(

                new_model,

                CURRENT_MODEL_PATH

            )

        decision = "DEPLOY_NEW_MODEL"

        status = "DEPLOYED"

        print(
            "New model deployed successfully."
        )

    else:

        print(
            "\nImprovement is not greater than 2%."
        )

        print(
            "Keeping current model."
        )

        decision = "KEEP_CURRENT_MODEL"

        status = "NOT_DEPLOYED"

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "status": status,

        "decision": decision,

        "current_f1": current_f1,

        "new_f1": new_f1,

        "improvement": improvement

    }