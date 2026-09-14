from fastapi import APIRouter

from ..models import JoinRequest, JoinResponse
from ..store import store


router = APIRouter(tags=["Participants"])


@router.post("/join/{token}", response_model=JoinResponse)
def join(token: str, request: JoinRequest) -> JoinResponse:
    session, participant, participant_token = store.join(token, request.displayName)
    return JoinResponse(session=session, participant=participant, participantToken=participant_token)
