from fastapi import APIRouter, Depends, Response, status

from ..models import (
    CandidateLink,
    CreateSessionRequest,
    Session,
    SessionSummary,
    UpdateSessionRequest,
)
from ..store import store
from .dependencies import current_user, session_reader


router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("", response_model=list[SessionSummary])
def list_sessions(_: object = Depends(current_user)) -> list[SessionSummary]:
    return store.list_sessions()


@router.post("", response_model=Session, status_code=status.HTTP_201_CREATED)
def create_session(request: CreateSessionRequest, _: object = Depends(current_user)) -> Session:
    return store.create_session(request)


@router.get("/{session_id}", response_model=Session)
def get_session(session_id: str, _: object = Depends(session_reader)) -> Session:
    return store.get_session(session_id)


@router.patch("/{session_id}", response_model=Session)
def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    _: object = Depends(current_user),
) -> Session:
    return store.update_session(session_id, request)


@router.post("/{session_id}/end", response_model=Session)
def end_session(session_id: str, _: object = Depends(current_user)) -> Session:
    return store.end_session(session_id)


@router.post("/{session_id}/duplicate", response_model=Session, status_code=status.HTTP_201_CREATED)
def duplicate_session(session_id: str, _: object = Depends(current_user)) -> Session:
    return store.duplicate_session(session_id)


@router.post("/{session_id}/candidate-link", response_model=CandidateLink, status_code=status.HTTP_201_CREATED)
def create_candidate_link(session_id: str, _: object = Depends(current_user)) -> CandidateLink:
    return store.create_candidate_link(session_id)


@router.delete("/{session_id}/candidate-link", response_model=CandidateLink | None)
def revoke_candidate_link(session_id: str, response: Response, _: object = Depends(current_user)) -> CandidateLink | None:
    link = store.revoke_candidate_link(session_id)
    if link is None:
        response.status_code = status.HTTP_200_OK
    return link
