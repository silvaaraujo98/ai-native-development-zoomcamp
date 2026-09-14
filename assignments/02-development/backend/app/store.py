from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, timedelta
from uuid import uuid4

from app.models import (
    Category,
    Column,
    ColumnId,
    Priority,
    Recurrence,
    Task,
    TaskCreate,
    TaskUpdate,
    UserRecord,
)


COLUMNS = [
    Column(id=ColumnId.TODO, label="To Do"),
    Column(id=ColumnId.DOING, label="Doing"),
    Column(id=ColumnId.PAUSED, label="Paused"),
    Column(id=ColumnId.DONE, label="Done"),
]


def _today() -> date:
    return date.today()


@dataclass
class InMemoryStore:
    users: dict[str, UserRecord] = field(default_factory=dict)
    users_by_username: dict[str, str] = field(default_factory=dict)
    tokens: dict[str, str] = field(default_factory=dict)
    tasks: dict[str, Task] = field(default_factory=dict)

    def reset(self, password_hash: str) -> None:
        self.users.clear()
        self.users_by_username.clear()
        self.tokens.clear()
        self.tasks.clear()

        user = UserRecord(
            id="user-1",
            name="Demo User",
            username="demo",
            password_hash=password_hash,
        )
        self.users[user.id] = user
        self.users_by_username[user.username] = user.id

        today = _today()
        self._seed_task(
            user.id,
            "task-1",
            "Review FastAPI contract",
            "Sketch the endpoints before integration starts.",
            today,
            Priority.HIGH,
            Category.PROJECT,
            Recurrence.NONE,
            ColumnId.TODO,
        )
        self._seed_task(
            user.id,
            "task-2",
            "Daily study block",
            "Spend 45 minutes on the course material.",
            today - timedelta(days=1),
            Priority.MEDIUM,
            Category.STUDY,
            Recurrence.DAILY,
            ColumnId.DOING,
        )
        self._seed_task(
            user.id,
            "task-3",
            "Plan demo recording",
            "Show login, create, drag, complete recurring, archive.",
            today + timedelta(days=3),
            Priority.LOW,
            Category.PROJECT,
            Recurrence.NONE,
            ColumnId.PAUSED,
        )
        self._seed_task(
            user.id,
            "task-4",
            "Clear inbox notes",
            "Keep this visible until manually archived.",
            today - timedelta(days=2),
            Priority.MEDIUM,
            Category.DAILY,
            Recurrence.WEEKLY,
            ColumnId.DONE,
            completed_at=today,
        )

    def _seed_task(
        self,
        user_id: str,
        task_id: str,
        title: str,
        notes: str,
        due_date: date,
        priority: Priority,
        category: Category,
        recurrence: Recurrence,
        column: ColumnId,
        completed_at: date | None = None,
    ) -> None:
        self.tasks[task_id] = Task(
            id=task_id,
            user_id=user_id,
            title=title,
            notes=notes,
            due_date=due_date,
            priority=priority,
            category=category,
            recurrence=recurrence,
            column=column,
            completed_at=completed_at,
        )

    def get_user_by_username(self, username: str) -> UserRecord | None:
        user_id = self.users_by_username.get(username)
        return deepcopy(self.users.get(user_id)) if user_id else None

    def save_token(self, token: str, user_id: str) -> None:
        self.tokens[token] = user_id

    def get_user_by_token(self, token: str) -> UserRecord | None:
        user_id = self.tokens.get(token)
        return deepcopy(self.users.get(user_id)) if user_id else None

    def list_active_tasks(self, user_id: str) -> list[Task]:
        self.auto_archive_done_tasks(user_id)
        return [
            deepcopy(task)
            for task in self.tasks.values()
            if task.user_id == user_id and not task.archived
        ]

    def get_task(self, user_id: str, task_id: str) -> Task | None:
        task = self.tasks.get(task_id)
        if task is None or task.user_id != user_id:
            return None
        return deepcopy(task)

    def create_task(self, user_id: str, payload: TaskCreate) -> Task:
        task = Task(
            id=f"task-{uuid4()}",
            user_id=user_id,
            title=payload.title,
            notes=payload.notes,
            due_date=payload.due_date,
            priority=payload.priority,
            category=payload.category,
            recurrence=payload.recurrence,
            column=ColumnId.TODO,
        )
        self.tasks[task.id] = task
        return deepcopy(task)

    def update_task(self, user_id: str, task_id: str, payload: TaskUpdate) -> Task | None:
        task = self.tasks.get(task_id)
        if task is None or task.user_id != user_id:
            return None
        updates = payload.model_dump(exclude_unset=True)
        for field_name, value in updates.items():
            setattr(task, field_name, value)
        if task.column != ColumnId.DONE:
            task.completed_at = None
        elif task.completed_at is None:
            task.completed_at = _today()
        return deepcopy(task)

    def delete_task(self, user_id: str, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task is None or task.user_id != user_id:
            return False
        del self.tasks[task_id]
        return True

    def move_task(self, user_id: str, task_id: str, column: ColumnId) -> Task | None:
        task = self.tasks.get(task_id)
        if task is None or task.user_id != user_id:
            return None

        previous_column = task.column
        task.column = column
        task.completed_at = _today() if column == ColumnId.DONE else None

        if (
            column == ColumnId.DONE
            and previous_column != ColumnId.DONE
            and task.recurrence != Recurrence.NONE
        ):
            self._create_next_recurring_task(task)

        return deepcopy(task)

    def _create_next_recurring_task(self, completed_task: Task) -> None:
        if completed_task.due_date is None:
            next_due_date = None
        else:
            days = 7 if completed_task.recurrence == Recurrence.WEEKLY else 1
            next_due_date = completed_task.due_date + timedelta(days=days)

        next_task = completed_task.model_copy(
            update={
                "id": f"task-{uuid4()}",
                "column": ColumnId.TODO,
                "due_date": next_due_date,
                "completed_at": None,
                "archived": False,
            }
        )
        self.tasks[next_task.id] = next_task

    def archive_task(self, user_id: str, task_id: str) -> Task | None:
        task = self.tasks.get(task_id)
        if task is None or task.user_id != user_id:
            return None
        task.archived = True
        return deepcopy(task)

    def auto_archive_done_tasks(self, user_id: str) -> None:
        cutoff = _today() - timedelta(days=7)
        for task in self.tasks.values():
            if (
                task.user_id == user_id
                and task.column == ColumnId.DONE
                and task.completed_at is not None
                and task.completed_at <= cutoff
            ):
                task.archived = True


store = InMemoryStore()
