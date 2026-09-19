from fastapi import APIRouter, Depends, status

from ..models import (
    AddConnectionRequest,
    AddElementRequest,
    AddStrokeRequest,
    Canvas,
    CanvasConnection,
    CanvasElement,
    CanvasStroke,
    UpdateElementRequest,
)
from ..store import store
from .dependencies import session_editor


router = APIRouter(prefix="/sessions/{session_id}/canvas", tags=["Canvas"])


@router.post("/elements", response_model=CanvasElement, status_code=status.HTTP_201_CREATED)
def add_element(
    session_id: str,
    request: AddElementRequest,
    _: object = Depends(session_editor),
) -> CanvasElement:
    return store.add_element(session_id, request)


@router.patch("/elements/{element_id}", response_model=CanvasElement)
def update_element(
    session_id: str,
    element_id: str,
    request: UpdateElementRequest,
    _: object = Depends(session_editor),
) -> CanvasElement:
    return store.update_element(session_id, element_id, request)


@router.delete("/elements/{element_id}", response_model=Canvas)
def delete_element(
    session_id: str,
    element_id: str,
    _: object = Depends(session_editor),
) -> Canvas:
    return store.delete_element(session_id, element_id)


@router.post("/connections", response_model=CanvasConnection, status_code=status.HTTP_201_CREATED)
def add_connection(
    session_id: str,
    request: AddConnectionRequest,
    _: object = Depends(session_editor),
) -> CanvasConnection:
    return store.add_connection(session_id, request)


@router.post("/strokes", response_model=CanvasStroke, status_code=status.HTTP_201_CREATED)
def add_stroke(
    session_id: str,
    request: AddStrokeRequest,
    _: object = Depends(session_editor),
) -> CanvasStroke:
    return store.add_stroke(session_id, request)
