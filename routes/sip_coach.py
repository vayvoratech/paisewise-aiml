from fastapi import APIRouter
from models.sip_coach import SIPCoachRequest, SIPCoachResponse
from services.sip_coach import coach_sip

router = APIRouter()


@router.post("/ai/sip-coach", response_model=SIPCoachResponse)
def sip_coach(request: SIPCoachRequest):
    return coach_sip(request.model_dump())
