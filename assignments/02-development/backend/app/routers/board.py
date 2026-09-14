from datetime import date

from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.models import BoardResponse, ColumnId, SummaryResponse, Task, UserRecord
from app.store import COLUMNS, store


router = APIRouter(tags=["board"])


def to_due_state(task: Task) -> str:
    if task.due_date is None or task.column == ColumnId.DONE:
        return ""
    today = date.today()
    if task.due_date == today:
        return "due_today"
    if task.due_date < today:
        return "overdue"
    return ""


@router.get("/board", response_model=BoardResponse)
def get_board(user: UserRecord = Depends(get_current_user)) -> BoardResponse:
    return BoardResponse(columns=COLUMNS, tasks=store.list_active_tasks(user.id))


@router.get("/dashboard/summary", response_model=SummaryResponse)
def get_summary(user: UserRecord = Depends(get_current_user)) -> SummaryResponse:
    tasks = store.list_active_tasks(user.id)
    return SummaryResponse(
        due_today=sum(1 for task in tasks if to_due_state(task) == "due_today"),
        overdue=sum(1 for task in tasks if to_due_state(task) == "overdue"),
        active_tasks=sum(1 for task in tasks if task.column != ColumnId.DONE),
        done_visible=sum(1 for task in tasks if task.column == ColumnId.DONE),
    )
