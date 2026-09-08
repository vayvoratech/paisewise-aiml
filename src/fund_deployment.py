import os
import shutil
import joblib

from fund_data import load_fund_data
from fund_scoring import calculate_scoring_weights
from fund_training import calculate_fund_scores


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_DIR = "../data/funds/models"

CURRENT_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "fund_recommendation_model.pkl"
)

NEW_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "new_fund_recommendation_model.pkl"
)


# ============================================================
# EVALUATE RECOMMENDATION MODEL
# ============================================================

def evaluate_model(model, test_data):

    weights = model["weights"]

    scored_data = calculate_fund_scores(
        test_data,
        weights
    )

    # --------------------------------------------------------
    # Create actual performance ranking
    # --------------------------------------------------------

    actual_data = test_data.copy()

    actual_data["actual_score"] = (
        (
            actual_data["return_1y"] /
            actual_data["return_1y"].max()
        )
        +
        (
            actual_data["return_3y"] /
            actual_data["return_3y"].max()
        )
    ) / 2

    actual_data["actual_rank"] = (
        actual_data["actual_score"]
        .rank(
            ascending=False,
            method="first"
        )
        .astype(int)
    )

    # --------------------------------------------------------
    # Merge predicted and actual rankings
    # --------------------------------------------------------

    comparison = scored_data[
        ["fund_name", "rank"]
    ].merge(
        actual_data[
            ["fund_name", "actual_rank"]
        ],
        on="fund_name"
    )

    # --------------------------------------------------------
    # Calculate ranking accuracy
    # --------------------------------------------------------

    ranking_matches = (
        comparison["rank"] ==
        comparison["actual_rank"]
    ).sum()

    ranking_accuracy = (
        ranking_matches /
        len(comparison)
    )

    return ranking_accuracy


# ============================================================
# DEPLOYMENT VALIDATION
# ============================================================

def validate_and_deploy(new_model):

    print("\n" + "=" * 60)
    print("FUND MODEL DEPLOYMENT VALIDATION")
    print("=" * 60)

    test_data = load_fund_data()

    # --------------------------------------------------------
    # Evaluate new model
    # --------------------------------------------------------

    new_score = evaluate_model(
        new_model,
        test_data
    )

    # --------------------------------------------------------
    # Evaluate current model
    # --------------------------------------------------------

    if os.path.exists(CURRENT_MODEL_PATH):

        print("\nCurrent model found.")

        current_model = joblib.load(
            CURRENT_MODEL_PATH
        )

        current_score = evaluate_model(
            current_model,
            test_data
        )

    else:

        print("\nNo current model found.")
        print("This is the first fund model deployment.")

        current_score = 0.0

    # --------------------------------------------------------
    # Calculate improvement
    # --------------------------------------------------------

    improvement = new_score - current_score

    print("\nCurrent model score:")
    print(f"{current_score:.2%}")

    print("\nNew model score:")
    print(f"{new_score:.2%}")

    print("\nImprovement:")
    print(f"{improvement:.2%}")

    # --------------------------------------------------------
    # Deployment rule
    # --------------------------------------------------------

    if not os.path.exists(CURRENT_MODEL_PATH):

        print("\nNo current model exists.")
        print("Deploying initial fund recommendation model.")

        os.makedirs(
            MODEL_DIR,
            exist_ok=True
        )

        shutil.copy2(
            NEW_MODEL_PATH,
            CURRENT_MODEL_PATH
        )

        decision = "INITIAL_DEPLOYMENT"
        status = "DEPLOYED"

    elif improvement > 0.02:

        print("\nImprovement is greater than 2%.")
        print("Deploying new fund recommendation model.")

        shutil.copy2(
            NEW_MODEL_PATH,
            CURRENT_MODEL_PATH
        )

        decision = "DEPLOY_NEW_MODEL"
        status = "DEPLOYED"

    else:

        print("\nImprovement is not greater than 2%.")
        print("Keeping current fund recommendation model.")

        decision = "KEEP_CURRENT_MODEL"
        status = "NOT_DEPLOYED"

    return {
        "status": status,
        "decision": decision,
        "current_score": current_score,
        "new_score": new_score,
        "improvement": improvement
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from fund_training import (
        train_fund_recommendation_model
    )

    result = train_fund_recommendation_model()

    deployment_result = validate_and_deploy(
        result["model"]
    )

    print("\n" + "=" * 60)
    print("FUND DEPLOYMENT VALIDATION COMPLETED")
    print("=" * 60)

    print(
        "Status:",
        deployment_result["status"]
    )

    print(
        "Decision:",
        deployment_result["decision"]
    )

    print(
        "Improvement:",
        f'{deployment_result["improvement"]:.2%}'
    )