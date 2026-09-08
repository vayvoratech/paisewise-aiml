import pandas as pd

from fund_data import load_fund_data


# ============================================================
# CALCULATE SCORING WEIGHTS
# ============================================================

def calculate_scoring_weights(data):

    print("\n" + "=" * 60)
    print("CALCULATING FUND SCORING WEIGHTS")
    print("=" * 60)

    # --------------------------------------------------------
    # Calculate average performance
    # --------------------------------------------------------

    avg_return_1y = data["return_1y"].mean()
    avg_return_3y = data["return_3y"].mean()

    avg_risk = data["risk_score"].mean()
    avg_consistency = data["consistency_score"].mean()

    print("\nAverage 1Y return:", round(avg_return_1y, 2))
    print("Average 3Y return:", round(avg_return_3y, 2))
    print("Average risk score:", round(avg_risk, 2))
    print(
        "Average consistency score:",
        round(avg_consistency, 2)
    )

    # --------------------------------------------------------
    # Normalize the factors
    # --------------------------------------------------------

    return_score = (
        avg_return_1y + avg_return_3y
    )

    risk_score = 10 - avg_risk

    consistency_score = avg_consistency

    total_score = (
        return_score
        + risk_score
        + consistency_score
    )

    # --------------------------------------------------------
    # Calculate dynamic weights
    # --------------------------------------------------------

    return_weight = return_score / total_score
    risk_weight = risk_score / total_score
    consistency_weight = consistency_score / total_score

    weights = {
        "return_weight": return_weight,
        "risk_weight": risk_weight,
        "consistency_weight": consistency_weight
    }

    print("\nCalculated scoring weights:")

    print(
        f"Return Weight       : {return_weight:.2%}"
    )

    print(
        f"Risk Weight         : {risk_weight:.2%}"
    )

    print(
        f"Consistency Weight  : {consistency_weight:.2%}"
    )

    print(
        "\nTotal Weight:",
        f"{sum(weights.values()):.2%}"
    )

    return weights


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    data = load_fund_data()

    weights = calculate_scoring_weights(data)

    print("\nScoring weights calculated successfully.")