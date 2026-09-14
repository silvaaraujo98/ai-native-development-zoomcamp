from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import count

from fastapi import HTTPException, status

from .auth import AuthPrincipal, hash_password, make_token, verify_password
from .models import (
    AddConnectionRequest,
    AddElementRequest,
    AddStrokeRequest,
    CandidateLink,
    Canvas,
    CanvasConnection,
    CanvasElement,
    CanvasElementType,
    CanvasStroke,
    ComponentDefault,
    CreateSessionRequest,
    Participant,
    ParticipantRole,
    Session,
    SessionState,
    SessionSummary,
    UpdateElementRequest,
    UpdateSessionRequest,
)


@dataclass
class User:
    id: str
    email: str
    password_hash: str


def now() -> datetime:
    return datetime.now(UTC)


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


class InterviewStore:
    def __init__(self) -> None:
        self._ids = count(1)
        self.component_defaults: dict[str, ComponentDefault] = {
            "service": ComponentDefault(label="Service", w=150, h=76, color="#d9e8ff"),
            "database": ComponentDefault(label="Database", w=132, h=86, color="#dff7e8"),
            "cache": ComponentDefault(label="Cache", w=126, h=72, color="#fff1c2"),
            "queue": ComponentDefault(label="Queue", w=138, h=72, color="#f1e3ff"),
            "gateway": ComponentDefault(label="API gateway", w=152, h=76, color="#d6f1ff"),
            "worker": ComponentDefault(label="Worker", w=132, h=76, color="#ffe2d3"),
            "client": ComponentDefault(label="Client", w=128, h=72, color="#e9edf5"),
            "vector": ComponentDefault(label="Vector DB", w=140, h=82, color="#d8fbf4"),
            "llm": ComponentDefault(label="LLM/model", w=142, h=76, color="#efe9ff"),
            "note": ComponentDefault(label="Assumption", w=160, h=110, color="#fff59d"),
        }
        self.users: dict[str, User] = {
            "user-demo": User(
                id="user-demo",
                email="interviewer@example.com",
                password_hash=hash_password("password123"),
            )
        }
        self.sessions: dict[str, Session] = {}
        self.access_tokens: dict[str, AuthPrincipal] = {}
        self.participant_tokens: dict[str, AuthPrincipal] = {}
        self.seed()

    def seed(self) -> None:
        created = datetime.fromisoformat("2026-08-03T14:00:00+00:00")
        updated = datetime.fromisoformat("2026-08-03T14:22:00+00:00")
        elements = [
            self._element("el-1", CanvasElementType.client, 70, 120, "Web clients"),
            self._element("el-2", CanvasElementType.gateway, 300, 120, "API gateway"),
            self._element("el-3", CanvasElementType.service, 540, 74, "Ingestion service"),
            self._element("el-4", CanvasElementType.queue, 780, 120, "Event stream"),
            self._element("el-5", CanvasElementType.worker, 540, 250, "Aggregation workers"),
            self._element("el-6", CanvasElementType.database, 780, 250, "Metrics store"),
            self._element("el-7", CanvasElementType.cache, 1010, 250, "Dashboard cache"),
            self._element("el-8", CanvasElementType.note, 90, 300, "Clarify peak write rate and retention window"),
        ]
        connections = [
            self._connection("conn-1", "el-1", "el-2", "HTTPS"),
            self._connection("conn-2", "el-2", "el-3", "validated events"),
            self._connection("conn-3", "el-3", "el-4", "append"),
            self._connection("conn-4", "el-4", "el-5", "consume"),
            self._connection("conn-5", "el-5", "el-6", "write"),
            self._connection("conn-6", "el-6", "el-7", "read-through"),
        ]
        session = Session(
            id="session-demo",
            title="Design a real-time analytics platform",
            prompt="Design a system that ingests user events, aggregates metrics in near real time, and exposes dashboards for product teams.",
            state=SessionState.live,
            candidateEditingEnabled=True,
            createdAt=created,
            updatedAt=updated,
            link=CandidateLink(token="candidate-demo-link", revokedAt=None, expiresAt=None, maxUses=10),
            participants=[
                Participant(id="p-owner", name="Maya", role=ParticipantRole.owner, color="#2563eb", active=True),
                Participant(id="p-candidate", name="Jordan", role=ParticipantRole.candidate, color="#059669", active=True),
                Participant(id="p-observer", name="Ravi", role=ParticipantRole.observer, color="#7c3aed", active=False),
            ],
            elementCount=len(elements),
            strokeCount=1,
            canvas=Canvas(
                elements=elements,
                connections=connections,
                strokes=[
                    CanvasStroke(id="stroke-1", color="#e11d48", width=4, points=[(520, 52), (645, 44), (705, 92)])
                ],
            ),
        )
        self.sessions[session.id] = session

    def authenticate_user(self, email: str, password: str) -> str | None:
        user = next((item for item in self.users.values() if item.email == email), None)
        if not user or not verify_password(password, user.password_hash):
            return None
        token = make_token("user")
        self.access_tokens[token] = AuthPrincipal(kind="user", subject=user.id)
        return token

    def principal_for_token(self, token: str) -> AuthPrincipal | None:
        return self.access_tokens.get(token) or self.participant_tokens.get(token)

    def list_sessions(self) -> list[SessionSummary]:
        return [self._summary(session) for session in self.sessions.values()]

    def get_session(self, session_id: str) -> Session:
        try:
            return deepcopy(self.sessions[session_id])
        except KeyError:
            raise api_error(status.HTTP_404_NOT_FOUND, "not_found", "Session not found")

    def create_session(self, request: CreateSessionRequest) -> Session:
        timestamp = now()
        session = Session(
            id=self._id("session"),
            title=request.title.strip(),
            prompt=request.prompt.strip(),
            state=SessionState.draft,
            candidateEditingEnabled=True,
            createdAt=timestamp,
            updatedAt=timestamp,
            link=None,
            participants=[
                Participant(id=self._id("p"), name="You", role=ParticipantRole.owner, color="#2563eb", active=True)
            ],
            elementCount=0,
            strokeCount=0,
            canvas=Canvas(elements=[], connections=[], strokes=[]),
        )
        self.sessions[session.id] = session
        return deepcopy(session)

    def update_session(self, session_id: str, request: UpdateSessionRequest) -> Session:
        session = self._session_ref(session_id)
        patch = request.model_dump(exclude_unset=True)
        for key, value in patch.items():
            setattr(session, key, value)
        session.updatedAt = now()
        self._refresh_counts(session)
        return deepcopy(session)

    def end_session(self, session_id: str) -> Session:
        session = self._session_ref(session_id)
        session.state = SessionState.ended
        session.endedAt = now()
        session.candidateEditingEnabled = False
        session.updatedAt = now()
        return deepcopy(session)

    def duplicate_session(self, session_id: str) -> Session:
        source = self._session_ref(session_id)
        duplicate = deepcopy(source)
        timestamp = now()
        duplicate.id = self._id("session")
        duplicate.title = f"{source.title} copy"
        duplicate.state = SessionState.draft
        duplicate.link = None
        duplicate.createdAt = timestamp
        duplicate.updatedAt = timestamp
        duplicate.startedAt = None
        duplicate.endedAt = None
        self.sessions[duplicate.id] = duplicate
        return deepcopy(duplicate)

    def create_candidate_link(self, session_id: str) -> CandidateLink:
        session = self._session_ref(session_id)
        session.link = CandidateLink(token=make_token("join").removeprefix("join_"), revokedAt=None, expiresAt=None, maxUses=10)
        session.updatedAt = now()
        return deepcopy(session.link)

    def revoke_candidate_link(self, session_id: str) -> CandidateLink | None:
        session = self._session_ref(session_id)
        if session.link:
            session.link.revokedAt = now()
        session.updatedAt = now()
        return deepcopy(session.link)

    def join(self, token: str, display_name: str) -> tuple[Session, Participant, str]:
        session = next((item for item in self.sessions.values() if item.link and item.link.token == token), None)
        if not session or session.link.revokedAt or session.state == SessionState.archived:
            raise api_error(status.HTTP_404_NOT_FOUND, "not_found", "This interview link is no longer available.")
        if session.state == SessionState.ended:
            raise api_error(status.HTTP_409_CONFLICT, "session_ended", "This interview has ended.")
        active_count = len([participant for participant in session.participants if participant.active])
        if session.link.maxUses is not None and active_count >= session.link.maxUses:
            raise api_error(status.HTTP_409_CONFLICT, "capacity_reached", "This interview is full.")
        participant = Participant(
            id=self._id("p"),
            name=display_name.strip(),
            role=ParticipantRole.candidate,
            color="#dc2626",
            active=True,
        )
        session.participants.append(participant)
        session.updatedAt = now()
        token_value = make_token("participant")
        self.participant_tokens[token_value] = AuthPrincipal(
            kind="participant",
            subject=participant.id,
            session_id=session.id,
        )
        return deepcopy(session), deepcopy(participant), token_value

    def add_element(self, session_id: str, request: AddElementRequest) -> CanvasElement:
        session = self._editable_session(session_id)
        element = self._element(self._id("el"), request.type, request.x, request.y)
        session.canvas.elements.append(element)
        self._touch_canvas(session)
        return deepcopy(element)

    def update_element(self, session_id: str, element_id: str, request: UpdateElementRequest) -> CanvasElement:
        session = self._editable_session(session_id)
        element = next((item for item in session.canvas.elements if item.id == element_id), None)
        if not element:
            raise api_error(status.HTTP_404_NOT_FOUND, "not_found", "Element not found")
        for key, value in request.model_dump(exclude_unset=True).items():
            setattr(element, key, value)
        self._touch_canvas(session)
        return deepcopy(element)

    def delete_element(self, session_id: str, element_id: str) -> Canvas:
        session = self._editable_session(session_id)
        if not any(item.id == element_id for item in session.canvas.elements):
            raise api_error(status.HTTP_404_NOT_FOUND, "not_found", "Element not found")
        session.canvas.elements = [item for item in session.canvas.elements if item.id != element_id]
        session.canvas.connections = [
            item for item in session.canvas.connections if item.from_ != element_id and item.to != element_id
        ]
        self._touch_canvas(session)
        return deepcopy(session.canvas)

    def add_connection(self, session_id: str, request: AddConnectionRequest) -> CanvasConnection:
        session = self._editable_session(session_id)
        ids = {element.id for element in session.canvas.elements}
        if request.from_ not in ids or request.to not in ids:
            raise api_error(status.HTTP_400_BAD_REQUEST, "invalid_connection", "Connection endpoints must exist.")
        connection = self._connection(self._id("conn"), request.from_, request.to, request.label)
        session.canvas.connections.append(connection)
        self._touch_canvas(session)
        return deepcopy(connection)

    def add_stroke(self, session_id: str, request: AddStrokeRequest) -> CanvasStroke:
        session = self._editable_session(session_id)
        stroke = CanvasStroke(id=self._id("stroke"), color=request.color, width=request.width, points=request.points)
        session.canvas.strokes.append(stroke)
        self._touch_canvas(session)
        return deepcopy(stroke)

    def can_access_session(self, principal: AuthPrincipal, session_id: str) -> bool:
        return principal.kind == "user" or principal.session_id == session_id

    def can_edit_session(self, principal: AuthPrincipal, session_id: str) -> bool:
        if principal.kind == "user":
            return True
        session = self._session_ref(session_id)
        return principal.session_id == session_id and session.candidateEditingEnabled and session.state != SessionState.ended

    def _session_ref(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            raise api_error(status.HTTP_404_NOT_FOUND, "not_found", "Session not found")
        return self.sessions[session_id]

    def _editable_session(self, session_id: str) -> Session:
        session = self._session_ref(session_id)
        if session.state == SessionState.ended:
            raise api_error(status.HTTP_403_FORBIDDEN, "forbidden", "Session is read-only.")
        return session

    def _element(self, element_id: str, type_: CanvasElementType, x: float, y: float, label: str | None = None) -> CanvasElement:
        defaults = self.component_defaults[type_.value]
        return CanvasElement(
            id=element_id,
            type=type_,
            x=x,
            y=y,
            w=defaults.w,
            h=defaults.h,
            label=label or defaults.label,
            color=defaults.color,
            description="",
        )

    def _connection(self, connection_id: str, from_id: str, to_id: str, label: str = "") -> CanvasConnection:
        return CanvasConnection(id=connection_id, from_=from_id, to=to_id, label=label, directed=True, style="solid")

    def _summary(self, session: Session) -> SessionSummary:
        self._refresh_counts(session)
        data = session.model_dump()
        data.pop("canvas")
        return SessionSummary.model_validate(data)

    def _touch_canvas(self, session: Session) -> None:
        session.updatedAt = now()
        self._refresh_counts(session)

    def _refresh_counts(self, session: Session) -> None:
        session.elementCount = len(session.canvas.elements)
        session.strokeCount = len(session.canvas.strokes)

    def _id(self, prefix: str) -> str:
        return f"{prefix}-{next(self._ids)}"


store = InterviewStore()
