from dataclasses import dataclass
from typing import Iterable

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from app.services.fraud_training_data_quality_service import (
    FraudTrainingDataQualityService,
)


@dataclass(frozen=True)
class FraudModelTrainingResult:
    model: LogisticRegression
    metrics: dict[str, float]
    training_samples: int
    validation_samples: int


class FraudModelTrainingService:
    """
    Trains the fraud-probability model from reviewed fraud cases.

    This service never creates or modifies fraud labels.
    """

    def __init__(
        self,
        quality_service: FraudTrainingDataQualityService,
        validation_size: float = 0.2,
        random_state: int = 42,
    ):
        if not 0 < validation_size < 1:
            raise ValueError(
                "validation_size must be between 0 and 1"
            )

        self.quality_service = quality_service
        self.validation_size = validation_size
        self.random_state = random_state

    def train(
        self,
        reviewed_cases: Iterable[dict],
    ) -> FraudModelTrainingResult:
        cases = list(reviewed_cases)

        quality = self.quality_service.validate(cases)

        if not quality.is_valid:
            raise ValueError(
                f"Fraud model training blocked: {quality.reason}"
            )

        features = []
        labels = []

        for case in cases:
            case_features = case.get("features")
            label = case.get("fraud_label")

            if case_features is None:
                raise ValueError(
                    "Training case is missing features"
                )

            if label not in (0, 1):
                raise ValueError(
                    "Training case contains an invalid fraud label"
                )

            features.append(case_features)
            labels.append(label)

        x = np.asarray(features, dtype=float)
        y = np.asarray(labels, dtype=int)

        if x.ndim != 2:
            raise ValueError(
                "Training features must be a 2D matrix"
            )

        if len(x) != len(y):
            raise ValueError(
                "Feature and label counts must match"
            )

        x_train, x_validation, y_train, y_validation = (
            train_test_split(
                x,
                y,
                test_size=self.validation_size,
                random_state=self.random_state,
                stratify=y,
            )
        )

        model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=self.random_state,
        )

        model.fit(x_train, y_train)

        predictions = model.predict(x_validation)
        probabilities = model.predict_proba(
            x_validation
        )[:, 1]

        metrics = {
            "accuracy": float(
                accuracy_score(
                    y_validation,
                    predictions,
                )
            ),
            "precision": float(
                precision_score(
                    y_validation,
                    predictions,
                    zero_division=0,
                )
            ),
            "recall": float(
                recall_score(
                    y_validation,
                    predictions,
                    zero_division=0,
                )
            ),
            "f1": float(
                f1_score(
                    y_validation,
                    predictions,
                    zero_division=0,
                )
            ),
            "roc_auc": float(
                roc_auc_score(
                    y_validation,
                    probabilities,
                )
            ),
        }

        return FraudModelTrainingResult(
            model=model,
            metrics=metrics,
            training_samples=len(x_train),
            validation_samples=len(x_validation),
        )