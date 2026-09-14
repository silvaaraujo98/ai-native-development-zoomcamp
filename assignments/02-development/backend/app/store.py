import os
from contextlib import contextmanager
from datetime import date, timedelta
from uuid import uuid4

from sqlalchemy import Boolean, Date, ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

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


DATABASE_URL_ENV = "DATABASE_URL"
DEFAULT_DATABASE_URL = "sqlite:///./focusboard.db"

COLUMNS = [
    Column(id=ColumnId.TODO, label="To Do"),
    Column(id=ColumnId.DOING, label="Doing"),
    Column(id=ColumnId.PAUSED, label="Paused"),
    Column(id=ColumnId.DONE, label="Done"),
]


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)


class TokenRow(Base):
    __tablename__ = "tokens"

    token: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)


class TaskRow(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str] = mapped_column(String, default="", nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    recurrence: Mapped[str] = mapped_column(String, nullable=False)
    column: Mapped[str] = mapped_column(String, nullable=False, index=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


def _today() -> date:
    return date.today()


def _database_url() -> str:
    return os.getenv(DATABASE_URL_ENV, DEFAULT_DATABASE_URL)


def _engine_kwargs(database_url: str) -> dict:
    if not database_url.startswith("sqlite"):
        return {}

    kwargs: dict = {"connect_args": {"check_same_thread": False}}
    if database_url in {"sqlite://", "sqlite:///:memory:"}:
        kwargs["poolclass"] = StaticPool
    return kwargs


def _user_from_row(row: UserRow | None) -> UserRecord | None:
    if row is None:
        return None
    return UserRecord(
        id=row.id,
        name=row.name,
        username=row.username,
        password_hash=row.password_hash,
    )


def _task_from_row(row: TaskRow) -> Task:
    return Task(
        id=row.id,
        user_id=row.user_id,
        title=row.title,
        notes=row.notes,
        due_date=row.due_date,
        priority=Priority(row.priority),
        category=Category(row.category),
        recurrence=Recurrence(row.recurrence),
        column=ColumnId(row.column),
        completed_at=row.completed_at,
        archived=row.archived,
    )


class SqlAlchemyStore:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or _database_url()
        self.engine = create_engine(self.database_url, **_engine_kwargs(self.database_url))
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.create_schema()

    @contextmanager
    def session(self):
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def create_schema(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    def drop_schema(self) -> None:
        Base.metadata.drop_all(bind=self.engine)

    def reset(self, password_hash: str) -> None:
        self.drop_schema()
        self.create_schema()

        with self.session() as db:
            user = UserRow(
                id="user-1",
                name="Demo User",
                username="demo",
                password_hash=password_hash,
            )
            db.add(user)

            today = _today()
            self._seed_task(
                db,
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
                db,
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
                db,
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
                db,
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
        db: Session,
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
        db.add(
            TaskRow(
                id=task_id,
                user_id=user_id,
                title=title,
                notes=notes,
                due_date=due_date,
                priority=priority.value,
                category=category.value,
                recurrence=recurrence.value,
                column=column.value,
                completed_at=completed_at,
            )
        )

    def get_user_by_username(self, username: str) -> UserRecord | None:
        with self.session() as db:
            row = db.scalar(select(UserRow).where(UserRow.username == username))
            return _user_from_row(row)

    def save_token(self, token: str, user_id: str) -> None:
        with self.session() as db:
            db.add(TokenRow(token=token, user_id=user_id))

    def get_user_by_token(self, token: str) -> UserRecord | None:
        with self.session() as db:
            token_row = db.get(TokenRow, token)
            if token_row is None:
                return None
            return _user_from_row(db.get(UserRow, token_row.user_id))

    def list_active_tasks(self, user_id: str) -> list[Task]:
        self.auto_archive_done_tasks(user_id)
        with self.session() as db:
            rows = db.scalars(
                select(TaskRow)
                .where(TaskRow.user_id == user_id, TaskRow.archived.is_(False))
                .order_by(TaskRow.id)
            ).all()
            return [_task_from_row(row) for row in rows]

    def get_task(self, user_id: str, task_id: str) -> Task | None:
        with self.session() as db:
            row = self._get_task_row(db, user_id, task_id)
            return _task_from_row(row) if row else None

    def create_task(self, user_id: str, payload: TaskCreate) -> Task:
        with self.session() as db:
            row = TaskRow(
                id=f"task-{uuid4()}",
                user_id=user_id,
                title=payload.title,
                notes=payload.notes,
                due_date=payload.due_date,
                priority=payload.priority.value,
                category=payload.category.value,
                recurrence=payload.recurrence.value,
                column=ColumnId.TODO.value,
            )
            db.add(row)
            db.flush()
            return _task_from_row(row)

    def update_task(self, user_id: str, task_id: str, payload: TaskUpdate) -> Task | None:
        with self.session() as db:
            row = self._get_task_row(db, user_id, task_id)
            if row is None:
                return None

            updates = payload.model_dump(exclude_unset=True)
            for field_name, value in updates.items():
                if value is None:
                    setattr(row, field_name, None)
                elif field_name in {"priority", "category", "recurrence", "column"}:
                    setattr(row, field_name, value.value)
                else:
                    setattr(row, field_name, value)

            if row.column != ColumnId.DONE.value:
                row.completed_at = None
            elif row.completed_at is None:
                row.completed_at = _today()

            db.flush()
            return _task_from_row(row)

    def delete_task(self, user_id: str, task_id: str) -> bool:
        with self.session() as db:
            row = self._get_task_row(db, user_id, task_id)
            if row is None:
                return False
            db.delete(row)
            return True

    def move_task(self, user_id: str, task_id: str, column: ColumnId) -> Task | None:
        with self.session() as db:
            row = self._get_task_row(db, user_id, task_id)
            if row is None:
                return None

            previous_column = ColumnId(row.column)
            row.column = column.value
            row.completed_at = _today() if column == ColumnId.DONE else None

            if (
                column == ColumnId.DONE
                and previous_column != ColumnId.DONE
                and Recurrence(row.recurrence) != Recurrence.NONE
            ):
                self._create_next_recurring_task(db, row)

            db.flush()
            return _task_from_row(row)

    def _create_next_recurring_task(self, db: Session, completed_task: TaskRow) -> None:
        if completed_task.due_date is None:
            next_due_date = None
        else:
            days = 7 if Recurrence(completed_task.recurrence) == Recurrence.WEEKLY else 1
            next_due_date = completed_task.due_date + timedelta(days=days)

        db.add(
            TaskRow(
                id=f"task-{uuid4()}",
                user_id=completed_task.user_id,
                title=completed_task.title,
                notes=completed_task.notes,
                due_date=next_due_date,
                priority=completed_task.priority,
                category=completed_task.category,
                recurrence=completed_task.recurrence,
                column=ColumnId.TODO.value,
                completed_at=None,
                archived=False,
            )
        )

    def archive_task(self, user_id: str, task_id: str) -> Task | None:
        with self.session() as db:
            row = self._get_task_row(db, user_id, task_id)
            if row is None:
                return None
            row.archived = True
            db.flush()
            return _task_from_row(row)

    def auto_archive_done_tasks(self, user_id: str) -> None:
        cutoff = _today() - timedelta(days=7)
        with self.session() as db:
            rows = db.scalars(
                select(TaskRow).where(
                    TaskRow.user_id == user_id,
                    TaskRow.column == ColumnId.DONE.value,
                    TaskRow.completed_at.is_not(None),
                    TaskRow.completed_at <= cutoff,
                )
            ).all()
            for row in rows:
                row.archived = True

    def set_task_completed_at(self, user_id: str, task_id: str, completed_at: date) -> None:
        with self.session() as db:
            row = self._get_task_row(db, user_id, task_id)
            if row is None:
                raise ValueError(f"Task {task_id} not found.")
            row.completed_at = completed_at

    def _get_task_row(self, db: Session, user_id: str, task_id: str) -> TaskRow | None:
        return db.scalar(
            select(TaskRow).where(TaskRow.id == task_id, TaskRow.user_id == user_id)
        )


store = SqlAlchemyStore()
