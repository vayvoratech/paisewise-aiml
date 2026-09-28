from dataclasses import dataclass

from app.services.fraud_model_training_service import (
    FraudModelTrainingResult,
    FraudModelTrainingService,
)
from app.services.fraud_training_data_quality_service import (
    FraudTrainingDataQuality,
    FraudTrainingDataQualityService,
)
from app.services.fraud_training_dataset_service import (
    FraudTrainingDatasetService,
)


@dataclass(frozen=True)
class FraudTrainingPipelineResult:
    training_result: FraudModelTrainingResult
    quality_result: FraudTrainingDataQuality


class FraudTrainingPipelineService:
    """
    Orchestrates the fraud training workflow.

    Repository access remains outside this service so that
    the orchestration logic can be tested independently.
    """

    def __init__(
        self,
        dataset_service: FraudTrainingDatasetService,
        quality_service: FraudTrainingDataQualityService,
        model_training_service: FraudModelTrainingService,
    ):
        if dataset_service is None:
            raise ValueError("dataset_service is required")

        if quality_service is None:
            raise ValueError("quality_service is required")

        if model_training_service is None:
            raise ValueError(
                "model_training_service is required"
            )

        self.dataset_service = dataset_service
        self.quality_service = quality_service
        self.model_training_service = model_training_service

    def train(
        self,
        reviewed_cases: list[dict],
        orders_by_id: dict,
    ) -> FraudTrainingPipelineResult:
        training_cases = self.dataset_service.build_dataset(
            reviewed_cases=reviewed_cases,
            orders_by_id=orders_by_id,
        )

        quality_result = self.quality_service.validate(
            training_cases
        )

        if not quality_result.is_valid:
            raise ValueError(
                f"Fraud training pipeline blocked: "
                f"{quality_result.reason}"
            )

        training_result = self.model_training_service.train(
            training_cases
        )

        return FraudTrainingPipelineResult(
            training_result=training_result,
            quality_result=quality_result,
        )