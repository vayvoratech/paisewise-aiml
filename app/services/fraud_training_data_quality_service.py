from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class FraudTrainingDataQuality:
    total_samples: int
    true_fraud_samples: int
    false_positive_samples: int
    is_valid: bool
    reason: str


class FraudTrainingDataQualityService:
    """
    Validates the final fraud training dataset before model training.

    fraud_label:
        1 = TRUE_FRAUD
        0 = FALSE_POSITIVE

    This service never creates or modifies labels.
    """

    def __init__(
        self,
        minimum_samples: int = 100,
    ):
        if minimum_samples < 2:
            raise ValueError(
                "minimum_samples must be at least 2"
            )

        self.minimum_samples = minimum_samples

    def validate(
        self,
        training_cases: Iterable[dict],
    ) -> FraudTrainingDataQuality:
        cases = list(training_cases)

        true_fraud = 0
        false_positive = 0

        for case in cases:
            label = case.get("fraud_label")

            if label == 1:
                true_fraud += 1
            elif label == 0:
                false_positive += 1
            else:
                raise ValueError(
                    "Training data contains a case without "
                    "a valid fraud label"
                )

        total = len(cases)

        if total < self.minimum_samples:
            return FraudTrainingDataQuality(
                total_samples=total,
                true_fraud_samples=true_fraud,
                false_positive_samples=false_positive,
                is_valid=False,
                reason=(
                    f"Insufficient reviewed fraud cases: "
                    f"{total} available, "
                    f"{self.minimum_samples} required"
                ),
            )

        if true_fraud == 0:
            return FraudTrainingDataQuality(
                total_samples=total,
                true_fraud_samples=true_fraud,
                false_positive_samples=false_positive,
                is_valid=False,
                reason=(
                    "Training data contains no TRUE_FRAUD samples"
                ),
            )

        if false_positive == 0:
            return FraudTrainingDataQuality(
                total_samples=total,
                true_fraud_samples=true_fraud,
                false_positive_samples=false_positive,
                is_valid=False,
                reason=(
                    "Training data contains no FALSE_POSITIVE samples"
                ),
            )

        return FraudTrainingDataQuality(
            total_samples=total,
            true_fraud_samples=true_fraud,
            false_positive_samples=false_positive,
            is_valid=True,
            reason="Training data is valid for model training",
        )