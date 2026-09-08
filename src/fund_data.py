import os
import pandas as pd

# ============================================================
# FUND DATA CONFIGURATION
# ============================================================

FUND_DATA_PATH = "../data/fund/fund_performance.csv"


# ============================================================
# LOAD FUND PERFORMANCE DATA
# ============================================================

def load_fund_data():

    print("=" * 60)
    print("LOADING FUND PERFORMANCE DATA")
    print("=" * 60)

    if not os.path.exists(FUND_DATA_PATH):
        raise FileNotFoundError(
            f"Fund performance dataset not found: {FUND_DATA_PATH}"
        )

    data = pd.read_csv(FUND_DATA_PATH)

    print("\nDataset loaded successfully.")
    print("Dataset shape:", data.shape)

    print("\nColumns:")
    print(data.columns.tolist())

    required_columns = [
        "fund_name",
        "category",
        "return_1y",
        "return_3y",
        "risk_score",
        "consistency_score"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    print("\nFund performance data:")
    print(data)

    return data


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    data = load_fund_data()

    print("\nFund data loaded successfully.")