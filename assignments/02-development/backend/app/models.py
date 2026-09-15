from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ColumnId(StrEnum):
    TODO = "todo"
    DOING = "doing"
    PAUSED = "paused"
    DONE = "done"


class Priority(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Category(StrEnum):
    DAILY = "Daily"
    PROJECT = "Project"
    STUDY = "Study"


class Recurrence(StrEnum):
    NONE = "None"
    DAILY = "Daily"
    WEEKLY = "Weekly"


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str


class UserRecord(UserPublic):
    username: str
    password_hash: str


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class Column(BaseModel):
    id: ColumnId
    label: str


class Subtask(BaseModel):
    id: str
    title: str = Field(min_length=1)
    completed: bool = False


class SubtaskInput(BaseModel):
    id: str | None = None
    title: str = Field(min_length=1)
    completed: bool = False


class TaskBase(BaseModel):
    title: str = Field(min_length=1)
    notes: str = ""
    due_date: date | None = None
    priority: Priority = Priority.MEDIUM
    category: Category = Category.DAILY
    recurrence: Recurrence = Recurrence.NONE


class TaskCreate(TaskBase):
    subtasks: list[SubtaskInput] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    notes: str | None = None
    due_date: date | None = None
    priority: Priority | None = None
    category: Category | None = None
    recurrence: Recurrence | None = None
    column: ColumnId | None = None
    subtasks: list[SubtaskInput] | None = None


class Task(TaskBase):
    id: str
    user_id: str
    column: ColumnId = ColumnId.TODO
    completed_at: date | None = None
    archived: bool = False
    subtasks: list[Subtask] = Field(default_factory=list)


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    column: ColumnId
    completed_at: date | None = None
    archived: bool = False
    subtasks: list[Subtask] = Field(default_factory=list)


class BoardResponse(BaseModel):
    columns: list[Column]
    tasks: list[TaskResponse]


class SummaryResponse(BaseModel):
    due_today: int
    overdue: int
    active_tasks: int
    done_visible: int


class MoveTaskRequest(BaseModel):
    column: ColumnId


class OkResponse(BaseModel):
    ok: bool = True
