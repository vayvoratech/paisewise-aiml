from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "tests"
    / "data"
    / "fraud_development_dataset.json"
)

ARTIFACT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "fraud_model_dev.joblib"
)

EXPECTED_FEATURE_COUNT = 7


def load_dataset() -> tuple[list[list[float]], list[int]]:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    if dataset.get("environment") != "development":
        raise ValueError(
            "Only the development dataset may be used "
            "by this script."
        )

    if dataset.get("data_source") != "synthetic":
        raise ValueError(
            "Expected a synthetic development dataset."
        )

    if dataset.get("production_use") is not False:
        raise ValueError(
            "Development synthetic data cannot be "
            "marked for production use."
        )

    feature_names = dataset.get("feature_names", [])

    if len(feature_names) != EXPECTED_FEATURE_COUNT:
        raise ValueError(
            "Expected exactly 7 fraud features."
        )

    features = []
    labels = []

    for record in dataset["records"]:
        record_features = record["features"]
        label = record["fraud_label"]

        if len(record_features) != EXPECTED_FEATURE_COUNT:
            raise ValueError(
                "Every record must contain exactly "
                "7 features."
            )

        if label not in (0, 1):
            raise ValueError(
                f"Invalid fraud label: {label}"
            )

        features.append(
            [float(value) for value in record_features]
        )
        labels.append(int(label))

    return features, labels


def train_model(
    features: list[list[float]],
    labels: list[int],
) -> LogisticRegression:

    (
        training_features,
        _,
        training_labels,
        _,
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

    return model


def main() -> None:
    print("=" * 60)
    print("TRAINING DEVELOPMENT FRAUD MODEL")
    print("=" * 60)

    features, labels = load_dataset()

    model = train_model(
        features,
        labels,
    )

    ARTIFACT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        ARTIFACT_PATH,
    )

    print()
    print(f"Dataset: {DATASET_PATH}")
    print(f"Samples: {len(features)}")
    print(f"Features: {len(features[0])}")
    print(f"Classes: {model.classes_.tolist()}")
    print(f"Artifact: {ARTIFACT_PATH}")

    print()
    print(
        "WARNING: This is a synthetic development "
        "model and is NOT production-ready."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()