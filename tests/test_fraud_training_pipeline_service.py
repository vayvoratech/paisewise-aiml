import pytest

from app.services.fraud_model_training_service import (
    FraudModelTrainingService,
)
from app.services.fraud_training_data_quality_service import (
    FraudTrainingDataQualityService,
)
from app.services.fraud_training_dataset_service import (
    FraudTrainingDatasetService,
)
from app.services.fraud_training_pipeline_service import (
    FraudTrainingPipelineService,
)


def build_order(order_id: str, index: int):
    return {
        "id": order_id,
        "shares": 20 if index >= 50 else 1,
        "price_per_share": 10000.0 if index >= 50 else 100.0,
        "total_amount": 200000.0 if index >= 50 else 100.0,
        "side": "SELL" if index >= 50 else "BUY",
        "order_type": "MARKET",
    }


def build_cases_and_orders():
    reviewed_cases = []
    orders_by_id = {}

    for index in range(100):
        order_id = f"order-{index}"

        decision = (
            "TRUE_FRAUD"
            if index >= 50
            else "FALSE_POSITIVE"
        )

        reviewed_cases.append(
            {
                "id": f"case-{index}",
                "order_id": order_id,
                "reviewer_decision": decision,
            }
        )

        orders_by_id[order_id] = build_order(
            order_id,
            index,
        )

    return reviewed_cases, orders_by_id


def build_service(minimum_samples=100):
    dataset_service = FraudTrainingDatasetService()

    quality_service = FraudTrainingDataQualityService(
        minimum_samples=minimum_samples
    )

    model_training_service = FraudModelTrainingService(
        quality_service=quality_service
    )

    return FraudTrainingPipelineService(
        dataset_service=dataset_service,
        quality_service=quality_service,
        model_training_service=model_training_service,
    )


def test_pipeline_trains_valid_dataset():
    service = build_service()

    reviewed_cases, orders_by_id = build_cases_and_orders()

    result = service.train(
        reviewed_cases=reviewed_cases,
        orders_by_id=orders_by_id,
    )

    assert result.quality_result.is_valid is True
    assert result.quality_result.total_samples == 100

    assert result.training_result.model is not None
    assert result.training_result.training_samples > 0
    assert result.training_result.validation_samples > 0


def test_pipeline_blocks_insufficient_dataset():
    service = build_service(minimum_samples=100)

    reviewed_cases, orders_by_id = build_cases_and_orders()

    reviewed_cases = reviewed_cases[:20]

    orders_by_id = {
        case["order_id"]: orders_by_id[case["order_id"]]
        for case in reviewed_cases
    }

    with pytest.raises(
        ValueError,
        match="Fraud training pipeline blocked",
    ):
        service.train(
            reviewed_cases=reviewed_cases,
            orders_by_id=orders_by_id,
        )


def test_pipeline_blocks_missing_order():
    service = build_service()

    reviewed_cases, _ = build_cases_and_orders()

    with pytest.raises(ValueError):
        service.train(
            reviewed_cases=reviewed_cases,
            orders_by_id={},
        )


def test_pipeline_requires_dependencies():
    dataset_service = FraudTrainingDatasetService()

    quality_service = FraudTrainingDataQualityService(
        minimum_samples=2
    )

    model_training_service = FraudModelTrainingService(
        quality_service=quality_service
    )

    with pytest.raises(ValueError):
        FraudTrainingPipelineService(
            dataset_service=None,
            quality_service=quality_service,
            model_training_service=model_training_service,
        )

    with pytest.raises(ValueError):
        FraudTrainingPipelineService(
            dataset_service=dataset_service,
            quality_service=None,
            model_training_service=model_training_service,
        )

    with pytest.raises(ValueError):
        FraudTrainingPipelineService(
            dataset_service=dataset_service,
            quality_service=quality_service,
            model_training_service=None,
        )