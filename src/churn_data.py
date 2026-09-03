import pandas as pd

# Churn Dataset Path

CHURN_DATA_PATH = "../data/churn/churn_training_dataset.csv"
# Load Churn Data

def load_churn_data():

    print("=" * 60)
    print("CHURN DATASET")
    print("=" * 60)

    # Load CSV
    data = pd.read_csv(
        CHURN_DATA_PATH
    )

    print("\nColumns in dataset:")
    print(data.columns.tolist())

    print("\nFirst 5 rows:")
    print(data.head())

    print("\nDataset shape:")
    print(data.shape)

    print("\nChurn distribution:")
    print(data["churned"].value_counts())

    return data

# Test this file directly

if __name__ == "__main__":

    data = load_churn_data()