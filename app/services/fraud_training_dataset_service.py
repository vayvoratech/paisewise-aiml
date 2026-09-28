from typing import Any

from app.services.fraud_feature_service import (
    FraudFeatureService,
)


class FraudTrainingDatasetService:
    """Builds labeled fraud-training records from reviewed fraud cases."""

    FRAUD_LABELS = {
        "TRUE_FRAUD": 1,
        "FALSE_POSITIVE": 0,
    }

    @classmethod
    def build_record(
        cls,
        fraud_case: dict[str, Any],
        order: dict[str, Any],
    ) -> dict[str, Any]:
        status = fraud_case.get("reviewer_decision")

        if status not in cls.FRAUD_LABELS:
            raise ValueError(
                "Only reviewed TRUE_FRAUD or FALSE_POSITIVE "
                "cases can be used for training"
            )

        features = FraudFeatureService.extract_features(order)

        return {
            "features": features,
            "fraud_label": cls.FRAUD_LABELS[status],
            "fraud_case_id": str(fraud_case["id"]),
            "order_id": str(order["id"]),
        }

    @classmethod
    def build_dataset(
        cls,
        reviewed_cases: list[dict[str, Any]],
        orders_by_id: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        dataset: list[dict[str, Any]] = []

        for fraud_case in reviewed_cases:
            order_id = str(fraud_case["order_id"])

            if order_id not in orders_by_id:
                raise ValueError(
                    f"Order not found for fraud case: {order_id}"
                )

            dataset.append(
                cls.build_record(
                    fraud_case,
                    orders_by_id[order_id],
                )
            )

        return dataset