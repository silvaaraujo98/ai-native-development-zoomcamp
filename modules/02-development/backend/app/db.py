import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DEFAULT_DATABASE_URL = "sqlite:///./interview.db"
DATABASE_URL_ENV = "INTERVIEW_DATABASE_URL"


def database_url() -> str:
    return os.getenv(DATABASE_URL_ENV, DEFAULT_DATABASE_URL)


class Base(DeclarativeBase):
    pass


def engine_kwargs(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


engine = create_engine(database_url(), future=True, **engine_kwargs(database_url()))
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def configure_database(url: str | None = None) -> None:
    global engine, SessionLocal
    selected_url = url or database_url()
    engine.dispose()
    engine = create_engine(selected_url, future=True, **engine_kwargs(selected_url))
    SessionLocal.configure(bind=engine)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
