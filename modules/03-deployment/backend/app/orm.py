from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)


class SessionRecord(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(String(40), nullable=False)
    candidate_editing_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    link_token: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    link_revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    link_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    link_max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    participants: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    elements: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    connections: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    strokes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)


class AccessTokenRecord(Base):
    __tablename__ = "access_tokens"

    token: Mapped[str] = mapped_column(String(255), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)


class ParticipantTokenRecord(Base):
    __tablename__ = "participant_tokens"

    token: Mapped[str] = mapped_column(String(255), primary_key=True)
    participant_id: Mapped[str] = mapped_column(String(80), nullable=False)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False)
