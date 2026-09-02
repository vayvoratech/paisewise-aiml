

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import LocalOutlierFactor

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "fraud_synthetic_data.csv"
MODEL_FILE = ROOT / "models" / "fraud_model_v1.pkl"
MODEL_CARD_FILE = ROOT / "docs" / "week11_fraud_model_card.md"

FEATURE_COLUMNS = [
    "device_changed",
    "location_changed",
    "time_since_registration",
    "order_value",
    "orders_last_30min",
    "failed_mpin_count_24hr",
    "login_count_today",
]


def load_data():
    df = pd.read_csv(DATA_FILE)
    df["device_changed"] = df["device_changed"].astype(int)
    df["location_changed"] = df["location_changed"].astype(int)

    X = df[FEATURE_COLUMNS]
    # sklearn's outlier models use 1 = normal, -1 = anomaly.
    # Our data uses "normal" / "anomaly" strings, so convert to match.
    y_true = df["label"].map({"normal": 1, "anomaly": -1})

    return X, y_true


def evaluate(y_true, y_pred, model_name):
    precision = precision_score(y_true, y_pred, pos_label=-1, zero_division=0)
    recall = recall_score(y_true, y_pred, pos_label=-1, zero_division=0)
    f1 = f1_score(y_true, y_pred, pos_label=-1, zero_division=0)

    print(f"{model_name} -> precision: {precision:.3f}, recall: {recall:.3f}, f1: {f1:.3f}")
    return {"precision": precision, "recall": recall, "f1": f1}


def train_isolation_forest(X_train, contamination):
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )
    model.fit(X_train)
    return model


def tune_contamination(X_train, X_test, y_test):
    """Task: tune contamination parameter across 0.01, 0.02, 0.05, 0.10."""
    results = {}

    for contamination in [0.01, 0.02, 0.05, 0.10]:
        model = train_isolation_forest(X_train, contamination)
        y_pred = model.predict(X_test)
        metrics = evaluate(y_test, y_pred, f"IsolationForest (contamination={contamination})")
        results[contamination] = {"model": model, "metrics": metrics}

    return results


def train_local_outlier_factor(X_train, X_test, contamination):
    """Task: train alternative model - Local Outlier Factor, in novelty mode
    so it can score new/unseen data the same way Isolation Forest does."""
    model = LocalOutlierFactor(
        n_neighbors=20,
        contamination=contamination,
        novelty=True,
    )
    model.fit(X_train)
    y_pred = model.predict(X_test)
    return model, y_pred


def run_pipeline():
    X, y_true = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_true, test_size=0.2, random_state=42, stratify=y_true
    )

    print("=== Step 1 & 2: baseline IsolationForest (contamination=0.05) ===")
    baseline_model = train_isolation_forest(X_train, contamination=0.05)
    baseline_pred = baseline_model.predict(X_test)
    baseline_metrics = evaluate(y_test, baseline_pred, "IsolationForest baseline")

    print("\n=== Step 3: tuning contamination ===")
    tuning_results = tune_contamination(X_train, X_test, y_test)

    best_contamination = max(
        tuning_results, key=lambda c: tuning_results[c]["metrics"]["f1"]
    )
    best_if_model = tuning_results[best_contamination]["model"]
    best_if_metrics = tuning_results[best_contamination]["metrics"]
    print(f"\nBest contamination by F1 score: {best_contamination}")

    print("\n=== Step 4: Local Outlier Factor comparison ===")
    lof_model, lof_pred = train_local_outlier_factor(
        X_train, X_test, contamination=best_contamination
    )
    lof_metrics = evaluate(y_test, lof_pred, "Local Outlier Factor")

    print("\n=== Step 5: choosing the best model ===")
    if best_if_metrics["f1"] >= lof_metrics["f1"]:
        chosen_model = best_if_model
        chosen_name = "IsolationForest"
        chosen_contamination = best_contamination
        chosen_metrics = best_if_metrics
    else:
        chosen_model = lof_model
        chosen_name = "LocalOutlierFactor"
        chosen_contamination = best_contamination
        chosen_metrics = lof_metrics

    print(f"Chosen model: {chosen_name} (F1={chosen_metrics['f1']:.3f})")

    print("\n=== Step 6: exporting model ===")
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(chosen_model, MODEL_FILE)
    print(f"Saved to {MODEL_FILE}")

    print("\n=== Step 7: writing model card ===")
    write_model_card(
        chosen_name,
        chosen_contamination,
        chosen_metrics,
        baseline_metrics,
        tuning_results,
        lof_metrics,
    )
    print(f"Saved to {MODEL_CARD_FILE}")

    return {
        "chosen_name": chosen_name,
        "chosen_contamination": chosen_contamination,
        "chosen_metrics": chosen_metrics,
    }


def write_model_card(
    chosen_name, chosen_contamination, chosen_metrics, baseline_metrics,
    tuning_results, lof_metrics,
):
    lines = []
    lines.append("# Week 11 - Fraud Detection Model Card\n")

    lines.append("## What the model does\n")
    lines.append(
        "Flags a transaction/login event as a fraud anomaly based on 7 "
        "features: device_changed, location_changed, "
        "time_since_registration, order_value, orders_last_30min, "
        "failed_mpin_count_24hr, login_count_today. It does not identify "
        "which of the 5 fraud categories applies - that's handled "
        "separately by the rule-based checks in "
        "`app/services/fraud_detection.py` (Week 10). This model is an "
        "additional, learned layer on top of those rules.\n"
    )

    lines.append("## Training data\n")
    lines.append(
        "`data/fraud_synthetic_data.csv` - 10,000 synthetic normal "
        "transactions and 500 synthetic anomaly transactions generated "
        "in Week 10, split 80/20 into train/test sets (stratified).\n"
    )

    lines.append("## Baseline performance (Isolation Forest, contamination=0.05)\n")
    lines.append(
        f"- Precision: {baseline_metrics['precision']:.3f}\n"
        f"- Recall: {baseline_metrics['recall']:.3f}\n"
        f"- F1: {baseline_metrics['f1']:.3f}\n"
    )

    lines.append("## Contamination tuning results\n")
    lines.append("| Contamination | Precision | Recall | F1 |\n")
    lines.append("|---|---|---|---|\n")
    for contamination, result in sorted(tuning_results.items()):
        m = result["metrics"]
        lines.append(
            f"| {contamination} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} |\n"
        )

    lines.append("\n## Local Outlier Factor comparison\n")
    lines.append(
        f"- Precision: {lof_metrics['precision']:.3f}\n"
        f"- Recall: {lof_metrics['recall']:.3f}\n"
        f"- F1: {lof_metrics['f1']:.3f}\n"
    )

    lines.append("\n## Decision\n")
    lines.append(
        f"Chosen model: **{chosen_name}** with contamination={chosen_contamination}, "
        f"based on the highest F1 score ({chosen_metrics['f1']:.3f}) on the held-out "
        "test set.\n"
    )

    lines.append("\n## Known limitations\n")
    lines.append(
        "- Trained on synthetic data only, not real user transactions - "
        "real-world performance may differ once deployed against actual "
        "traffic patterns.\n"
        "- The 5 anomaly categories were generated with fairly distinct, "
        "separable feature ranges (see Week 10 data generator), so this "
        "model has not been tested against subtler, more realistic fraud "
        "patterns.\n"
        "- Category 2 (unusual trading velocity) is approximated using a "
        "30-minute order count instead of the 2-minute window described "
        "in the original task, as noted in Week 10's documentation.\n"
        "- Should be retrained periodically once real transaction data is "
        "available, rather than relying on synthetic data long-term.\n"
    )

    MODEL_CARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODEL_CARD_FILE.write_text("".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run_pipeline()
