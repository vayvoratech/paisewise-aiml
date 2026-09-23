import os
import pandas as pd


# ============================================================
# PAISEWISE CHURN DATA
# ============================================================

CHURN_DATA_PATH = "../data/churn/churn_training_dataset.csv"


# ============================================================
# LOAD CHURN DATA
# ============================================================

def load_churn_data():

    print("=" * 60)
    print("LOADING CHURN DATASET")
    print("=" * 60)

    # --------------------------------------------------------
    # Check dataset
    # --------------------------------------------------------

    if not os.path.exists(CHURN_DATA_PATH):

        raise FileNotFoundError(
            f"Churn dataset not found: {CHURN_DATA_PATH}"
        )

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    data = pd.read_csv(CHURN_DATA_PATH)

    print("\nDataset loaded successfully.")

    print(
        "Dataset shape:",
        data.shape
    )

    # --------------------------------------------------------
    # Display columns
    # --------------------------------------------------------

    print("\nColumns:")

    print(
        data.columns.tolist()
    )

    # --------------------------------------------------------
    # Validate target
    # --------------------------------------------------------

    if "churned" not in data.columns:

        raise ValueError(
            "Target column 'churned' is missing."
        )

    # --------------------------------------------------------
    # Churn distribution
    # --------------------------------------------------------

    print("\nChurn distribution:")

    print(
        data["churned"].value_counts()
    )

    # ========================================================
    # 90-DAY FILTER
    # ========================================================
    #
    # Current sample dataset has no date column.
    #
    # Therefore we use the complete dataset.
    #
    # If future production data contains one of the supported
    # date columns, the last 90 days will automatically be used.
    # ========================================================

    possible_date_columns = [

        "outcome_date",

        "churn_date",

        "activity_date",

        "created_at"

    ]

    date_column = None

    for column in possible_date_columns:

        if column in data.columns:

            date_column = column

            break

    # --------------------------------------------------------
    # Date available
    # --------------------------------------------------------

    if date_column is not None:

        print(
            f"\nDate column detected: {date_column}"
        )

        data[date_column] = pd.to_datetime(

            data[date_column],

            errors="coerce"

        )

        # Remove invalid dates

        data = data.dropna(
            subset=[date_column]
        )

        if len(data) == 0:

            raise ValueError(
                "No valid dates found in dataset."
            )

        # Latest date available

        latest_date = data[date_column].max()

        # 90-day cutoff

        cutoff_date = (

            latest_date

            - pd.Timedelta(days=90)

        )

        # Filter

        data = data[
            data[date_column] >= cutoff_date
        ]

        print("\n90-day data window:")

        print(
            "From:",
            cutoff_date.date()
        )

        print(
            "To:",
            latest_date.date()
        )

        print(
            "Records after 90-day filter:",
            len(data)
        )

    # --------------------------------------------------------
    # No date available
    # --------------------------------------------------------

    else:

        print("\nWARNING")

        print("-" * 60)

        print(
            "No date column found in dataset."
        )

        print(
            "Using complete dataset for testing."
        )

        print(
            "Real 90-day filtering will be applied "
            "when dated production data is available."
        )

        print("-" * 60)

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return data


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    data = load_churn_data()

    print("\nFirst 5 rows:")

    print(
        data.head()
    )