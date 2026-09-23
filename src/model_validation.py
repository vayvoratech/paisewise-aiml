
# PaiseWise Fund Recommendation Model Validation
# Step 3: Validate new model against current model

from fund_data import fetch_latest_fund_data
from fund_scoring import (
    calculate_scoring_weights,
    calculate_fund_scores
)


# --------------------------------------------------
# Current model weights
# --------------------------------------------------

CURRENT_MODEL_WEIGHTS = {

    "return_1y": 0.30,

    "return_3y": 0.25,

    "risk": 0.20,

    "sharpe_ratio": 0.15,

    "expense_ratio": 0.10
}


# --------------------------------------------------
# Calculate model performance
# --------------------------------------------------

def calculate_model_performance(
    scored_funds
):

    if scored_funds.empty:

        raise ValueError(
            "No fund data available for validation."
        )

    # Average fund score is used as the
    # validation performance metric

    performance = (
        scored_funds["fund_score"].mean()
    )

    return float(performance)


# --------------------------------------------------
# Validate current vs new model
# --------------------------------------------------

def validate_models():

    print("=" * 60)
    print("PaiseWise Model Validation")
    print("=" * 60)

    # ----------------------------------------------
    # Step 1: Load test data
    # ----------------------------------------------

    test_data = fetch_latest_fund_data()

    print()
    print(
        "Test funds:",
        len(test_data)
    )

    # ----------------------------------------------
    # Step 2: Calculate new model weights
    # ----------------------------------------------

    new_weights = calculate_scoring_weights(
        test_data
    )

    print()
    print("New model weights:")

    for factor, weight in new_weights.items():

        print(
            f"{factor}: {weight:.2%}"
        )

    # ----------------------------------------------
    # Step 3: Score using current model
    # ----------------------------------------------

    current_scores = calculate_fund_scores(
        test_data,
        CURRENT_MODEL_WEIGHTS
    )

    # ----------------------------------------------
    # Step 4: Score using new model
    # ----------------------------------------------

    new_scores = calculate_fund_scores(
        test_data,
        new_weights
    )

    # ----------------------------------------------
    # Step 5: Calculate performance
    # ----------------------------------------------

    current_performance = (
        calculate_model_performance(
            current_scores
        )
    )

    new_performance = (
        calculate_model_performance(
            new_scores
        )
    )

    # ----------------------------------------------
    # Step 6: Calculate improvement
    # ----------------------------------------------

    if current_performance == 0:

        improvement = 0

    else:

        improvement = (
            (new_performance - current_performance)
            / abs(current_performance)
        )

    # ----------------------------------------------
    # Step 7: Display results
    # ----------------------------------------------

    print()
    print("Model Performance:")
    print(
        f"Current model: "
        f"{current_performance:.4f}"
    )

    print(
        f"New model: "
        f"{new_performance:.4f}"
    )

    print(
        f"Improvement: "
        f"{improvement:.2%}"
    )

    # ----------------------------------------------
    # Step 8: Deployment decision
    # ----------------------------------------------

    if improvement > 0.02:

        decision = "DEPLOY_NEW_MODEL"

    else:

        decision = "KEEP_CURRENT_MODEL"

    print()
    print(
        "Decision:",
        decision
    )

    print()
    print(
        "Model validation completed successfully."
    )

    return {

        "current_model_performance":
            round(
                current_performance,
                4
            ),

        "new_model_performance":
            round(
                new_performance,
                4
            ),

        "improvement":
            round(
                improvement,
                4
            ),

        "decision":
            decision
    }


# --------------------------------------------------
# Run validation
# --------------------------------------------------

if __name__ == "__main__":

    result = validate_models()

    print()
    print("Validation Result:")
    print(result)

