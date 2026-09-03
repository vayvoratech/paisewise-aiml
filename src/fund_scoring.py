

import pandas as pd

from fund_data import fetch_latest_fund_data


def normalize_series(series):

    minimum = series.min()
    maximum = series.max()

    # Avoid division by zero
    if maximum == minimum:
        return pd.Series(
            [1.0] * len(series),
            index=series.index
        )

    return (
        (series - minimum) /
        (maximum - minimum)
    )


def calculate_scoring_weights(data):

    # ---------------------------------------------
    # Normalize fund performance factors
    # ---------------------------------------------

    return_score = normalize_series(
        data["return_1y"]
    )

    long_term_score = normalize_series(
        data["return_3y"]
    )

    risk_score = 1 - normalize_series(
        data["risk"]
    )

    sharpe_score = normalize_series(
        data["sharpe_ratio"]
    )

    expense_score = 1 - normalize_series(
        data["expense_ratio"]
    )

    # ---------------------------------------------
    # Calculate average performance of each factor
    # ---------------------------------------------

    factor_scores = {

        "return_1y": return_score.mean(),

        "return_3y": long_term_score.mean(),

        "risk": risk_score.mean(),

        "sharpe_ratio": sharpe_score.mean(),

        "expense_ratio": expense_score.mean()
    }

    # ---------------------------------------------
    # Convert factor scores into weights
    # ---------------------------------------------

    total_score = sum(
        factor_scores.values()
    )

    if total_score == 0:
        raise ValueError(
            "Unable to calculate scoring weights."
        )

    weights = {

        factor: round(
            score / total_score,
            4
        )

        for factor, score
        in factor_scores.items()
    }

    return weights


def calculate_fund_scores(
    data,
    weights
):

    scored_data = data.copy()

    # Normalize each factor

    scored_data["return_1y_score"] = (
        normalize_series(
            scored_data["return_1y"]
        )
    )

    scored_data["return_3y_score"] = (
        normalize_series(
            scored_data["return_3y"]
        )
    )

    # Lower risk is better

    scored_data["risk_score"] = (
        1 -
        normalize_series(
            scored_data["risk"]
        )
    )

    scored_data["sharpe_score"] = (
        normalize_series(
            scored_data["sharpe_ratio"]
        )
    )

    # Lower expense ratio is better

    scored_data["expense_score"] = (
        1 -
        normalize_series(
            scored_data["expense_ratio"]
        )
    )

    # ---------------------------------------------
    # Final fund score
    # ---------------------------------------------

    scored_data["fund_score"] = (

        scored_data["return_1y_score"]
        * weights["return_1y"]

        +

        scored_data["return_3y_score"]
        * weights["return_3y"]

        +

        scored_data["risk_score"]
        * weights["risk"]

        +

        scored_data["sharpe_score"]
        * weights["sharpe_ratio"]

        +

        scored_data["expense_score"]
        * weights["expense_ratio"]
    )

    return scored_data


if __name__ == "__main__":

    print("=" * 60)
    print("PaiseWise Fund Scoring")
    print("=" * 60)

    # ---------------------------------------------
    # Step 1: Load latest fund data
    # ---------------------------------------------

    funds = fetch_latest_fund_data()

    print()
    print(
        "Funds loaded:",
        len(funds)
    )

    # ---------------------------------------------
    # Step 2: Calculate new weights
    # ---------------------------------------------

    weights = calculate_scoring_weights(
        funds
    )

    print()
    print("Recalculated scoring weights:")

    for factor, weight in weights.items():

        print(
            f"{factor}: {weight:.2%}"
        )

    # ---------------------------------------------
    # Step 3: Calculate fund scores
    # ---------------------------------------------

    scored_funds = calculate_fund_scores(
        funds,
        weights
    )

    print()
    print("Fund scores:")

    result = scored_funds[
        ["fund_name", "fund_score"]
    ].sort_values(
        by="fund_score",
        ascending=False
    )

    print(result.to_string(index=False))

    print()
    print(
        "Scoring weights recalculated successfully."
    )
