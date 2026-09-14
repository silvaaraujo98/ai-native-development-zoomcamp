from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    code: str
    message: str


class ComponentDefault(BaseModel):
    label: str
    w: int = Field(gt=0)
    h: int = Field(gt=0)
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")


class SessionState(StrEnum):
    draft = "draft"
    live = "live"
    ended = "ended"
    archived = "archived"


class ParticipantRole(StrEnum):
    owner = "Owner"
    interviewer = "Interviewer"
    candidate = "Candidate"
    observer = "Observer"


class CanvasElementType(StrEnum):
    service = "service"
    database = "database"
    cache = "cache"
    queue = "queue"
    gateway = "gateway"
    worker = "worker"
    client = "client"
    vector = "vector"
    llm = "llm"
    note = "note"


class CandidateLink(BaseModel):
    token: str
    revokedAt: datetime | None
    expiresAt: datetime | None
    maxUses: int | None = Field(default=None, ge=1)


class Participant(BaseModel):
    id: str
    name: str
    role: ParticipantRole
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    active: bool


class CanvasElement(BaseModel):
    id: str
    type: CanvasElementType
    x: float
    y: float
    w: float = Field(gt=0)
    h: float = Field(gt=0)
    label: str
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    description: str


class CanvasConnection(BaseModel):
    id: str
    from_: str = Field(alias="from")
    to: str
    label: str
    directed: bool
    style: str = Field(pattern=r"^(solid|dashed)$")

    model_config = ConfigDict(populate_by_name=True)


Point = Annotated[tuple[float, float], Field(min_length=2, max_length=2)]


class CanvasStroke(BaseModel):
    id: str
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    width: float = Field(ge=1)
    points: list[Point] = Field(min_length=2)


class Canvas(BaseModel):
    elements: list[CanvasElement]
    connections: list[CanvasConnection]
    strokes: list[CanvasStroke]


class SessionSummary(BaseModel):
    id: str
    title: str
    prompt: str
    state: SessionState
    candidateEditingEnabled: bool
    createdAt: datetime
    updatedAt: datetime
    startedAt: datetime | None = None
    endedAt: datetime | None = None
    link: CandidateLink | None
    participants: list[Participant]
    elementCount: int = Field(ge=0)
    strokeCount: int = Field(ge=0)


class Session(SessionSummary):
    canvas: Canvas


class CreateSessionRequest(BaseModel):
    title: str = Field(min_length=1)
    prompt: str = Field(min_length=1)


class UpdateSessionRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    prompt: str | None = None
    state: SessionState | None = None
    candidateEditingEnabled: bool | None = None
    endedAt: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class JoinRequest(BaseModel):
    displayName: str = Field(min_length=1)


class JoinResponse(BaseModel):
    session: Session
    participant: Participant
    participantToken: str


class AddElementRequest(BaseModel):
    type: CanvasElementType
    x: float
    y: float


class UpdateElementRequest(BaseModel):
    type: CanvasElementType | None = None
    x: float | None = None
    y: float | None = None
    w: float | None = Field(default=None, gt=0)
    h: float | None = Field(default=None, gt=0)
    label: str | None = None
    color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    description: str | None = None

    model_config = ConfigDict(extra="forbid")


class AddConnectionRequest(BaseModel):
    from_: str = Field(alias="from")
    to: str
    label: str = ""

    model_config = ConfigDict(populate_by_name=True)


class AddStrokeRequest(BaseModel):
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    width: float = Field(ge=1)
    points: list[Point] = Field(min_length=2)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
