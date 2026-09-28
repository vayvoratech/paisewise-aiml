from __future__ import annotations

import json
from pathlib import Path

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


EXPECTED_FEATURES = [
    "shares",
    "price_per_share",
    "total_amount",
    "side_buy",
    "side_sell",
    "order_type_market",
    "order_type_limit",
]


def load_dataset() -> dict:
    """Load and validate the synthetic development dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Fraud development dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if dataset.get("environment") != "development":
        raise ValueError(
            "Training is restricted to the development dataset."
        )

    if dataset.get("data_source") != "synthetic":
        raise ValueError(
            "This training script expects synthetic development data."
        )

    if dataset.get("production_use") is not False:
        raise ValueError(
            "Synthetic development data must not be marked for production use."
        )

    if dataset.get("feature_names") != EXPECTED_FEATURES:
        raise ValueError(
            "Dataset feature schema does not match the expected 7-feature schema."
        )

    records = dataset.get("records", [])

    if not records:
        raise ValueError("Dataset contains no records.")

    return dataset


def prepare_data(dataset: dict) -> tuple[list[list[float]], list[int]]:
    """Extract feature vectors and fraud labels."""

    features = []
    labels = []

    for record in dataset["records"]:
        record_features = record.get("features")
        fraud_label = record.get("fraud_label")

        if not isinstance(record_features, list):
            raise ValueError(
                f"Invalid feature vector for case {record.get('case_id')}"
            )

        if len(record_features) != len(EXPECTED_FEATURES):
            raise ValueError(
                f"Case {record.get('case_id')} does not contain "
                f"{len(EXPECTED_FEATURES)} features."
            )

        if fraud_label not in (0, 1):
            raise ValueError(
                f"Invalid fraud label for case {record.get('case_id')}: "
                f"{fraud_label}"
            )

        features.append(
            [float(value) for value in record_features]
        )
        labels.append(int(fraud_label))

    return features, labels


def train_model(
    features: list[list[float]],
    labels: list[int],
) -> tuple[LogisticRegression, dict[str, float], int, int]:
    """Train and evaluate the development fraud model."""

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

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )

    model.fit(
        training_features,
        training_labels,
    )

    predictions = model.predict(validation_features)
    probabilities = model.predict_proba(validation_features)[:, 1]

    metrics = {
        "accuracy": float(
            accuracy_score(validation_labels, predictions)
        ),
        "precision": float(
            precision_score(
                validation_labels,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                validation_labels,
                predictions,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                validation_labels,
                predictions,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                validation_labels,
                probabilities,
            )
        ),
    }

    return (
        model,
        metrics,
        len(training_features),
        len(validation_features),
    )


def main() -> None:
    print("=" * 60)
    print("FRAUD DEVELOPMENT MODEL TRAINING")
    print("=" * 60)

    dataset = load_dataset()

    features, labels = prepare_data(dataset)

    (
        model,
        metrics,
        training_samples,
        validation_samples,
    ) = train_model(
        features,
        labels,
    )

    print()
    print(f"Dataset: {DATASET_PATH}")
    print(f"Environment: {dataset['environment']}")
    print(f"Data source: {dataset['data_source']}")
    print(f"Production use: {dataset['production_use']}")
    print(f"Features: {len(EXPECTED_FEATURES)}")
    print(f"Training samples: {training_samples}")
    print(f"Validation samples: {validation_samples}")

    print()
    print("Validation Metrics")
    print("-" * 30)
    print(f"ACCURACY  : {metrics['accuracy']:.4f}")
    print(f"PRECISION : {metrics['precision']:.4f}")
    print(f"RECALL    : {metrics['recall']:.4f}")
    print(f"F1        : {metrics['f1']:.4f}")
    print(f"ROC_AUC   : {metrics['roc_auc']:.4f}")

    print()
    print(f"Model classes: {model.classes_.tolist()}")

    print()
    print(
        "NOTE: This model was trained on synthetic development data "
        "and is NOT a production fraud model."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()