from __future__ import annotations

import json
from pathlib import Path

from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "tests"
    / "data"
    / "fraud_development_dataset.json"
)


def load_dataset():
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    if dataset.get("feature_names") is None:
        raise ValueError("Dataset feature schema is missing.")

    if len(dataset["feature_names"]) != 7:
        raise ValueError("Benchmark requires exactly 7 features.")

    features = [
        record["features"]
        for record in dataset["records"]
    ]

    labels = [
        record["fraud_label"]
        for record in dataset["records"]
    ]

    return features, labels


def evaluate_model(
    name,
    model,
    training_features,
    validation_features,
    training_labels,
    validation_labels,
):
    model.fit(
        training_features,
        training_labels,
    )

    predictions = model.predict(
        validation_features
    )

    probabilities = model.predict_proba(
        validation_features
    )[:, 1]

    metrics = {
        "accuracy": accuracy_score(
            validation_labels,
            predictions,
        ),
        "precision": precision_score(
            validation_labels,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            validation_labels,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            validation_labels,
            predictions,
            zero_division=0,
        ),
        "roc_auc": roc_auc_score(
            validation_labels,
            probabilities,
        ),
    }

    print()
    print(name)
    print("-" * len(name))

    print(
        f"ACCURACY  : {metrics['accuracy']:.4f}"
    )
    print(
        f"PRECISION : {metrics['precision']:.4f}"
    )
    print(
        f"RECALL    : {metrics['recall']:.4f}"
    )
    print(
        f"F1        : {metrics['f1']:.4f}"
    )
    print(
        f"ROC_AUC   : {metrics['roc_auc']:.4f}"
    )

    return model, metrics


def main():
    print("=" * 60)
    print("7-FEATURE FRAUD MODEL BENCHMARK")
    print("=" * 60)

    features, labels = load_dataset()

    (
        training_features,
        validation_features,
        training_labels,
        validation_labels,
    ) = train_test_split(
        features,
        labels,
        test_size=0.20,
        random_state=42,
        stratify=labels,
    )

    models = [
        (
            "Logistic Regression",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
        (
            "Random Forest",
            RandomForestClassifier(
                n_estimators=100,
                max_depth=8,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42,
                n_jobs=1,
            ),
        ),
        (
            "HistGradientBoosting",
            HistGradientBoostingClassifier(
                max_iter=100,
                max_leaf_nodes=15,
                learning_rate=0.05,
                random_state=42,
            ),
        ),
    ]

    results = []

    for name, model in models:
        trained_model, metrics = evaluate_model(
            name,
            model,
            training_features,
            validation_features,
            training_labels,
            validation_labels,
        )

        results.append(
            {
                "name": name,
                "model": trained_model,
                "metrics": metrics,
            }
        )

    print()
    print("=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)

    for result in results:
        metrics = result["metrics"]

        print(
            f"{result['name']:<25} "
            f"ROC-AUC={metrics['roc_auc']:.4f} "
            f"F1={metrics['f1']:.4f}"
        )

    print()
    print(
        "All models use the same seven transaction features."
    )
    print(
        "Dataset is synthetic development data; "
        "results are not production validation."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()