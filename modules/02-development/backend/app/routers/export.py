from fastapi import APIRouter, Depends

from ..models import Session
from ..store import store
from .dependencies import current_user


router = APIRouter(prefix="/sessions", tags=["Export"])


@router.get("/{session_id}/export.json", response_model=Session)
def export_session_json(session_id: str, _: object = Depends(current_user)) -> Session:
    return store.get_session(session_id)
