from fastapi import APIRouter, HTTPException

from app.repositories.fraud_case_repository import FraudCaseRepository
from app.schemas.fraud_case import (
    FraudCaseDecisionRequest,
    FraudCaseDecisionResponse,
)


router = APIRouter(
    prefix="/fraud/cases",
    tags=["Fraud Case Management"],
)


@router.post(
    "/{case_id}/decision",
    response_model=FraudCaseDecisionResponse,
)
async def update_fraud_case_decision(
    case_id: str,
    request: FraudCaseDecisionRequest,
) -> FraudCaseDecisionResponse:
    repository = FraudCaseRepository()

    case = repository.get_case(case_id)

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Fraud case not found",
        )

    if case["status"] != "PENDING_REVIEW":
        raise HTTPException(
            status_code=409,
            detail="Fraud case has already been reviewed",
        )

    updated_case = repository.update_reviewer_decision(
        case_id=case_id,
        decision=request.decision,
    )

    if updated_case is None:
        raise HTTPException(
            status_code=404,
            detail="Fraud case not found",
        )

    return FraudCaseDecisionResponse(
        case_id=str(updated_case["id"]),
        order_id=str(updated_case["order_id"]),
        decision=updated_case["reviewer_decision"],
        status=updated_case["status"],
    )