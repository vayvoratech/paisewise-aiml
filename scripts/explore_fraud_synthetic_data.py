
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # no display needed, we just save PNG files
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "fraud_synthetic_data.csv"
PLOTS_DIR = ROOT / "data" / "fraud_plots"

NUMERIC_FEATURES = [
    "time_since_registration",
    "order_value",
    "orders_last_30min",
    "failed_mpin_count_24hr",
    "login_count_today",
]

BOOLEAN_FEATURES = [
    "device_changed",
    "location_changed",
]


def load_data(input_file=INPUT_FILE):
    df = pd.read_csv(input_file)
    df["device_changed"] = df["device_changed"].astype(bool)
    df["location_changed"] = df["location_changed"].astype(bool)
    return df


def plot_numeric_feature(df, feature, output_dir):
    normal_values = df[df["label"] == "normal"][feature]
    anomaly_values = df[df["label"] == "anomaly"][feature]

    plt.figure(figsize=(7, 4))
    plt.hist(normal_values, bins=30, alpha=0.6, label="normal", color="#4C72B0")
    plt.hist(anomaly_values, bins=30, alpha=0.6, label="anomaly", color="#C44E52")
    plt.title(f"{feature}: normal vs anomaly")
    plt.xlabel(feature)
    plt.ylabel("count")
    plt.legend()
    plt.tight_layout()

    output_path = output_dir / f"{feature}.png"
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_boolean_feature(df, feature, output_dir):
    proportions = (
        df.groupby("label")[feature]
        .mean()  # fraction of True values in each group
        .reindex(["normal", "anomaly"])
    )

    plt.figure(figsize=(5, 4))
    plt.bar(proportions.index, proportions.values, color=["#4C72B0", "#C44E52"])
    plt.title(f"{feature}: proportion True, normal vs anomaly")
    plt.ylabel("proportion True")
    plt.ylim(0, 1)
    plt.tight_layout()

    output_path = output_dir / f"{feature}.png"
    plt.savefig(output_path)
    plt.close()
    return output_path


def explore(input_file=INPUT_FILE, output_dir=PLOTS_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    df = load_data(input_file)

    saved_paths = []

    for feature in NUMERIC_FEATURES:
        saved_paths.append(plot_numeric_feature(df, feature, output_dir))

    for feature in BOOLEAN_FEATURES:
        saved_paths.append(plot_boolean_feature(df, feature, output_dir))

    print(f"Saved {len(saved_paths)} plots to {output_dir}")
    for path in saved_paths:
        print(f" - {path.name}")

    return saved_paths


if __name__ == "__main__":
    explore()
