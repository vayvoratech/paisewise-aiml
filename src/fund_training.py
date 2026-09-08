import os
import joblib
import pandas as pd

from fund_data import load_fund_data
from fund_scoring import calculate_scoring_weights

# ============================================================
# CONFIGURATION
# ============================================================

MODEL_DIR = "../data/funds/models"

NEW_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "new_fund_recommendation_model.pkl"
)


# ============================================================
# CALCULATE FUND SCORES
# ============================================================

def calculate_fund_scores(data, weights):

    print("\n" + "=" * 60)
    print("CALCULATING FUND SCORES")
    print("=" * 60)

    # --------------------------------------------------------
    # Normalize return values
    # --------------------------------------------------------

    max_return_1y = data["return_1y"].max()
    max_return_3y = data["return_3y"].max()

    max_consistency = data["consistency_score"].max()
    max_risk = data["risk_score"].max()

    data = data.copy()

    # --------------------------------------------------------
    # Create normalized scores
    # --------------------------------------------------------

    data["return_score"] = (
        (
            data["return_1y"] / max_return_1y
        )
        +
        (
            data["return_3y"] / max_return_3y
        )
    ) / 2

    data["risk_score_normalized"] = (
        1 -
        (
            data["risk_score"] / max_risk
        )
    )

    data["consistency_score_normalized"] = (
        data["consistency_score"] /
        max_consistency
    )

    # --------------------------------------------------------
    # Calculate final recommendation score
    # --------------------------------------------------------

    data["fund_score"] = (
        data["return_score"] *
        weights["return_weight"]
        +
        data["risk_score_normalized"] *
        weights["risk_weight"]
        +
        data["consistency_score_normalized"] *
        weights["consistency_weight"]
    )

    # --------------------------------------------------------
    # Rank funds
    # --------------------------------------------------------

    data["rank"] = (
        data["fund_score"]
        .rank(
            ascending=False,
            method="first"
        )
        .astype(int)
    )

    data = data.sort_values(
        "fund_score",
        ascending=False
    )

    print("\nFund ranking:")

    print(
        data[
            [
                "fund_name",
                "category",
                "fund_score",
                "rank"
            ]
        ].to_string(index=False)
    )

    return data


# ============================================================
# TRAIN NEW FUND RECOMMENDATION MODEL
# ============================================================

def train_fund_recommendation_model():

    print("\n" + "=" * 60)
    print("TRAINING NEW FUND RECOMMENDATION MODEL")
    print("=" * 60)

    # --------------------------------------------------------
    # Step 1: Load latest fund data
    # --------------------------------------------------------

    data = load_fund_data()

    # --------------------------------------------------------
    # Step 2: Calculate dynamic weights
    # --------------------------------------------------------

    weights = calculate_scoring_weights(data)

    # --------------------------------------------------------
    # Step 3: Calculate fund scores
    # --------------------------------------------------------

    scored_data = calculate_fund_scores(
        data,
        weights
    )

    # --------------------------------------------------------
    # Save model information
    # --------------------------------------------------------

    model = {
        "weights": weights,
        "fund_scores": scored_data[
            [
                "fund_name",
                "category",
                "fund_score",
                "rank"
            ]
        ]
    }

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    joblib.dump(
        model,
        NEW_MODEL_PATH
    )

    print("\nNew fund recommendation model saved:")
    print(NEW_MODEL_PATH)

    # --------------------------------------------------------
    # Display top recommendations
    # --------------------------------------------------------

    print("\nTop 5 fund recommendations:")

    top_funds = scored_data.head(5)

    for index, row in top_funds.iterrows():

        print(
            f"{row['rank']}. "
            f"{row['fund_name']} "
            f"-> Score: {row['fund_score']:.4f}"
        )

    return {
        "model": model,
        "weights": weights,
        "scored_data": scored_data,
        "model_path": NEW_MODEL_PATH
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = train_fund_recommendation_model()

    print(
        "\nFund recommendation training "
        "completed successfully."
    )