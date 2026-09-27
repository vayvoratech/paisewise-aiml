from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.sip_coach import future_value_of_sip, required_monthly_sip

router = APIRouter()


class SIPScenarioRequest(BaseModel):
    monthlySIP: float = Field(gt=0)
    months: int = Field(gt=0)
    annualReturn: float = Field(default=10.0, ge=0, le=30)
    currentAmount: float = Field(default=0, ge=0)
    targetAmount: float | None = Field(default=None, gt=0)


@router.post("/ai/sip-scenario")
def sip_scenario(request: SIPScenarioRequest):
    projected = future_value_of_sip(request.monthlySIP, request.months, request.annualReturn)
    result = {
        "monthlySIP": request.monthlySIP,
        "months": request.months,
        "annualReturnAssumption": request.annualReturn,
        "projectedAmount": round(projected, 2),
    }
    if request.targetAmount is not None:
        result["requiredMonthlySIP"] = round(required_monthly_sip(request.targetAmount, request.currentAmount, request.months, request.annualReturn), 2)
    return result
