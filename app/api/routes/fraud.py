from fastapi import APIRouter, HTTPException

from app.repositories.fraud_order_repository import FraudOrderRepository
from app.schemas.fraud import FraudScoreRequest, FraudScoreResponse
from app.services.fraud_decision_policy import FraudDecisionPolicy
from app.services.fraud_model_service import FraudModelService
from app.services.fraud_runtime import fraud_runtime
from app.services.fraud_scoring_service import FraudScoringService


router = APIRouter(
    prefix="/fraud",
    tags=["Fraud Scoring"],
)


@router.post(
    "/score",
    response_model=FraudScoreResponse,
)
async def score_fraud(
    request: FraudScoreRequest,
) -> FraudScoreResponse:
    repository = FraudOrderRepository()

    order = repository.get_order_by_id(request.order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    # Use the model already loaded into memory during application startup.
    try:
        runtime = fraud_runtime.get_runtime()
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="Fraud model is not configured",
        )

    model_service = FraudModelService(runtime.model)

    # Thresholds are supplied through the decision policy.
    # These values are temporary test configuration until
    # production thresholds are established from validated data.
    decision_policy = FraudDecisionPolicy(
        review_threshold=0.50,
        block_threshold=0.80,
    )

    scoring_service = FraudScoringService(
        model_service=model_service,
        decision_policy=decision_policy,
    )

    try:
        result = scoring_service.score_order(order)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return FraudScoreResponse(
        order_id=str(order["id"]),
        fraud_probability=result.fraud_probability,
        decision=result.decision.value,
    )