
# PaiseWise Fund Performance Data

import pandas as pd


def fetch_latest_fund_data():

    data = pd.read_csv(
        "../data/fund/fund_performance.csv"
    )

    if data.empty:
        raise ValueError(
            "Fund performance dataset is empty."
        )

    data = data.drop_duplicates(
        subset=["fund_name"]
    )

    required_columns = [
        "fund_name",
        "return_1y",
        "return_3y",
        "risk",
        "sharpe_ratio",
        "expense_ratio"
    ]

    data = data.dropna(
        subset=required_columns
    )

    return data


if __name__ == "__main__":

    print("=" * 60)
    print("PaiseWise Fund Performance Data")
    print("=" * 60)

    try:

        funds = fetch_latest_fund_data()

        print(
            "Funds loaded:",
            len(funds)
        )

        print()
        print(funds.head())

        print()
        print(
            "Fund data loaded successfully."
        )

    except Exception as e:

        print(
            f"Failed to load fund data: {str(e)}"
        )
