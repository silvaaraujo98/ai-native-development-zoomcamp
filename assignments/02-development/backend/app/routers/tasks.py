from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.models import (
    MoveTaskRequest,
    OkResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    UserRecord,
)
from app.store import HighPriorityDailyLimitError, store


router = APIRouter(prefix="/tasks", tags=["tasks"])


def not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")


def high_priority_limit_reached(exc: HighPriorityDailyLimitError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    user: UserRecord = Depends(get_current_user),
) -> TaskResponse:
    try:
        return store.create_task(user.id, payload)
    except HighPriorityDailyLimitError as exc:
        raise high_priority_limit_reached(exc) from exc


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    user: UserRecord = Depends(get_current_user),
) -> TaskResponse:
    try:
        task = store.update_task(user.id, task_id, payload)
    except HighPriorityDailyLimitError as exc:
        raise high_priority_limit_reached(exc) from exc
    if task is None:
        raise not_found()
    return task


@router.delete("/{task_id}", response_model=OkResponse)
def delete_task(task_id: str, user: UserRecord = Depends(get_current_user)) -> OkResponse:
    if not store.delete_task(user.id, task_id):
        raise not_found()
    return OkResponse()


@router.post("/{task_id}/move", response_model=TaskResponse)
def move_task(
    task_id: str,
    payload: MoveTaskRequest,
    user: UserRecord = Depends(get_current_user),
) -> TaskResponse:
    try:
        task = store.move_task(user.id, task_id, payload.column)
    except HighPriorityDailyLimitError as exc:
        raise high_priority_limit_reached(exc) from exc
    if task is None:
        raise not_found()
    return task


@router.post("/{task_id}/archive", response_model=TaskResponse)
def archive_task(task_id: str, user: UserRecord = Depends(get_current_user)) -> TaskResponse:
    task = store.archive_task(user.id, task_id)
    if task is None:
        raise not_found()
    return task
