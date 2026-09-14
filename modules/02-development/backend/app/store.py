from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session as DbSession

from .auth import AuthPrincipal, hash_password, make_token, verify_password
from .db import Base, engine, session_scope
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
from .orm import AccessTokenRecord, ParticipantTokenRecord, SessionRecord, UserRecord


def now() -> datetime:
    return datetime.now(UTC)


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def dump_model(model) -> dict:
    return model.model_dump(mode="json", by_alias=True)


class InterviewStore:
    def __init__(self) -> None:
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
        self.create_schema()
        self.seed_if_empty()

    def create_schema(self) -> None:
        Base.metadata.create_all(bind=engine)

    def reset(self) -> None:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.seed_if_empty()

    def seed_if_empty(self) -> None:
        with session_scope() as db:
            if db.scalar(select(UserRecord.id).limit(1)):
                return
            db.add(
                UserRecord(
                    id="user-demo",
                    email="interviewer@example.com",
                    password_hash=hash_password("password123"),
                )
            )
            db.add(self._seed_session_record())

    def authenticate_user(self, email: str, password: str) -> str | None:
        with session_scope() as db:
            user = db.scalar(select(UserRecord).where(UserRecord.email == email))
            if not user or not verify_password(password, user.password_hash):
                return None
            token = make_token("user")
            db.add(AccessTokenRecord(token=token, user_id=user.id))
            return token

    def principal_for_token(self, token: str) -> AuthPrincipal | None:
        with session_scope() as db:
            access = db.get(AccessTokenRecord, token)
            if access:
                return AuthPrincipal(kind="user", subject=access.user_id)
            participant = db.get(ParticipantTokenRecord, token)
            if participant:
                return AuthPrincipal(
                    kind="participant",
                    subject=participant.participant_id,
                    session_id=participant.session_id,
                )
            return None

    def list_sessions(self) -> list[SessionSummary]:
        with session_scope() as db:
            records = db.scalars(select(SessionRecord).order_by(SessionRecord.updated_at.desc())).all()
            return [self._summary_from_record(record) for record in records]

    def get_session(self, session_id: str) -> Session:
        with session_scope() as db:
            return self._session_from_record(self._session_ref(db, session_id))

    def create_session(self, request: CreateSessionRequest) -> Session:
        timestamp = now()
        record = SessionRecord(
            id=self._id("session"),
            title=request.title.strip(),
            prompt=request.prompt.strip(),
            state=SessionState.draft.value,
            candidate_editing_enabled=True,
            created_at=timestamp,
            updated_at=timestamp,
            participants=[
                dump_model(Participant(id=self._id("p"), name="You", role=ParticipantRole.owner, color="#2563eb", active=True))
            ],
            elements=[],
            connections=[],
            strokes=[],
        )
        with session_scope() as db:
            db.add(record)
            db.flush()
            return self._session_from_record(record)

    def update_session(self, session_id: str, request: UpdateSessionRequest) -> Session:
        with session_scope() as db:
            record = self._session_ref(db, session_id)
            patch = request.model_dump(exclude_unset=True)
            for key, value in patch.items():
                if key == "candidateEditingEnabled":
                    record.candidate_editing_enabled = value
                elif key == "endedAt":
                    record.ended_at = value
                else:
                    setattr(record, key, value.value if isinstance(value, SessionState) else value)
            record.updated_at = now()
            db.flush()
            return self._session_from_record(record)

    def end_session(self, session_id: str) -> Session:
        with session_scope() as db:
            record = self._session_ref(db, session_id)
            record.state = SessionState.ended.value
            record.ended_at = now()
            record.candidate_editing_enabled = False
            record.updated_at = now()
            db.flush()
            return self._session_from_record(record)

    def duplicate_session(self, session_id: str) -> Session:
        with session_scope() as db:
            source = self._session_ref(db, session_id)
            timestamp = now()
            duplicate = SessionRecord(
                id=self._id("session"),
                title=f"{source.title} copy",
                prompt=source.prompt,
                state=SessionState.draft.value,
                candidate_editing_enabled=source.candidate_editing_enabled,
                created_at=timestamp,
                updated_at=timestamp,
                participants=list(source.participants),
                elements=list(source.elements),
                connections=list(source.connections),
                strokes=list(source.strokes),
            )
            db.add(duplicate)
            db.flush()
            return self._session_from_record(duplicate)

    def create_candidate_link(self, session_id: str) -> CandidateLink:
        with session_scope() as db:
            record = self._session_ref(db, session_id)
            record.link_token = make_token("join").removeprefix("join_")
            record.link_revoked_at = None
            record.link_expires_at = None
            record.link_max_uses = 10
            record.updated_at = now()
            db.flush()
            return self._link_from_record(record)

    def revoke_candidate_link(self, session_id: str) -> CandidateLink | None:
        with session_scope() as db:
            record = self._session_ref(db, session_id)
            if record.link_token:
                record.link_revoked_at = now()
            record.updated_at = now()
            db.flush()
            return self._link_from_record(record) if record.link_token else None

    def join(self, token: str, display_name: str) -> tuple[Session, Participant, str]:
        with session_scope() as db:
            record = db.scalar(select(SessionRecord).where(SessionRecord.link_token == token))
            if not record or record.link_revoked_at or record.state == SessionState.archived.value:
                raise api_error(status.HTTP_404_NOT_FOUND, "not_found", "This interview link is no longer available.")
            if record.state == SessionState.ended.value:
                raise api_error(status.HTTP_409_CONFLICT, "session_ended", "This interview has ended.")
            participants = list(record.participants)
            active_count = len([participant for participant in participants if participant["active"]])
            if record.link_max_uses is not None and active_count >= record.link_max_uses:
                raise api_error(status.HTTP_409_CONFLICT, "capacity_reached", "This interview is full.")
            participant = Participant(
                id=self._id("p"),
                name=display_name.strip(),
                role=ParticipantRole.candidate,
                color="#dc2626",
                active=True,
            )
            participants.append(dump_model(participant))
            record.participants = participants
            record.updated_at = now()
            token_value = make_token("participant")
            db.add(ParticipantTokenRecord(token=token_value, participant_id=participant.id, session_id=record.id))
            db.flush()
            return self._session_from_record(record), participant, token_value

    def add_element(self, session_id: str, request: AddElementRequest) -> CanvasElement:
        with session_scope() as db:
            record = self._editable_session(db, session_id)
            element = self._element(self._id("el"), request.type, request.x, request.y)
            record.elements = [*record.elements, dump_model(element)]
            self._touch(record)
            db.flush()
            return element

    def update_element(self, session_id: str, element_id: str, request: UpdateElementRequest) -> CanvasElement:
        with session_scope() as db:
            record = self._editable_session(db, session_id)
            elements = list(record.elements)
            index = next((i for i, item in enumerate(elements) if item["id"] == element_id), None)
            if index is None:
                raise api_error(status.HTTP_404_NOT_FOUND, "not_found", "Element not found")
            patch = request.model_dump(mode="json", exclude_unset=True)
            elements[index] = {**elements[index], **patch}
            record.elements = elements
            self._touch(record)
            db.flush()
            return CanvasElement.model_validate(elements[index])

    def delete_element(self, session_id: str, element_id: str) -> Canvas:
        with session_scope() as db:
            record = self._editable_session(db, session_id)
            if not any(item["id"] == element_id for item in record.elements):
                raise api_error(status.HTTP_404_NOT_FOUND, "not_found", "Element not found")
            record.elements = [item for item in record.elements if item["id"] != element_id]
            record.connections = [
                item for item in record.connections if item["from"] != element_id and item["to"] != element_id
            ]
            self._touch(record)
            db.flush()
            return self._canvas_from_record(record)

    def add_connection(self, session_id: str, request: AddConnectionRequest) -> CanvasConnection:
        with session_scope() as db:
            record = self._editable_session(db, session_id)
            ids = {element["id"] for element in record.elements}
            if request.from_ not in ids or request.to not in ids:
                raise api_error(status.HTTP_400_BAD_REQUEST, "invalid_connection", "Connection endpoints must exist.")
            connection = self._connection(self._id("conn"), request.from_, request.to, request.label)
            record.connections = [*record.connections, dump_model(connection)]
            self._touch(record)
            db.flush()
            return connection

    def add_stroke(self, session_id: str, request: AddStrokeRequest) -> CanvasStroke:
        with session_scope() as db:
            record = self._editable_session(db, session_id)
            stroke = CanvasStroke(id=self._id("stroke"), color=request.color, width=request.width, points=request.points)
            record.strokes = [*record.strokes, dump_model(stroke)]
            self._touch(record)
            db.flush()
            return stroke

    def can_access_session(self, principal: AuthPrincipal, session_id: str) -> bool:
        return principal.kind == "user" or principal.session_id == session_id

    def can_edit_session(self, principal: AuthPrincipal, session_id: str) -> bool:
        if principal.kind == "user":
            return True
        with session_scope() as db:
            record = self._session_ref(db, session_id)
            return (
                principal.session_id == session_id
                and record.candidate_editing_enabled
                and record.state != SessionState.ended.value
            )

    def _session_ref(self, db: DbSession, session_id: str) -> SessionRecord:
        record = db.get(SessionRecord, session_id)
        if not record:
            raise api_error(status.HTTP_404_NOT_FOUND, "not_found", "Session not found")
        return record

    def _editable_session(self, db: DbSession, session_id: str) -> SessionRecord:
        record = self._session_ref(db, session_id)
        if record.state == SessionState.ended.value:
            raise api_error(status.HTTP_403_FORBIDDEN, "forbidden", "Session is read-only.")
        return record

    def _seed_session_record(self) -> SessionRecord:
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
        participants = [
            Participant(id="p-owner", name="Maya", role=ParticipantRole.owner, color="#2563eb", active=True),
            Participant(id="p-candidate", name="Jordan", role=ParticipantRole.candidate, color="#059669", active=True),
            Participant(id="p-observer", name="Ravi", role=ParticipantRole.observer, color="#7c3aed", active=False),
        ]
        strokes = [CanvasStroke(id="stroke-1", color="#e11d48", width=4, points=[(520, 52), (645, 44), (705, 92)])]
        return SessionRecord(
            id="session-demo",
            title="Design a real-time analytics platform",
            prompt="Design a system that ingests user events, aggregates metrics in near real time, and exposes dashboards for product teams.",
            state=SessionState.live.value,
            candidate_editing_enabled=True,
            created_at=created,
            updated_at=updated,
            link_token="candidate-demo-link",
            link_max_uses=10,
            participants=[dump_model(participant) for participant in participants],
            elements=[dump_model(element) for element in elements],
            connections=[dump_model(connection) for connection in connections],
            strokes=[dump_model(stroke) for stroke in strokes],
        )

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

    def _summary_from_record(self, record: SessionRecord) -> SessionSummary:
        data = self._session_from_record(record).model_dump()
        data.pop("canvas")
        return SessionSummary.model_validate(data)

    def _session_from_record(self, record: SessionRecord) -> Session:
        canvas = self._canvas_from_record(record)
        return Session(
            id=record.id,
            title=record.title,
            prompt=record.prompt,
            state=SessionState(record.state),
            candidateEditingEnabled=record.candidate_editing_enabled,
            createdAt=record.created_at,
            updatedAt=record.updated_at,
            startedAt=record.started_at,
            endedAt=record.ended_at,
            link=self._link_from_record(record) if record.link_token else None,
            participants=[Participant.model_validate(item) for item in record.participants],
            elementCount=len(canvas.elements),
            strokeCount=len(canvas.strokes),
            canvas=canvas,
        )

    def _canvas_from_record(self, record: SessionRecord) -> Canvas:
        return Canvas(
            elements=[CanvasElement.model_validate(item) for item in record.elements],
            connections=[CanvasConnection.model_validate(item) for item in record.connections],
            strokes=[CanvasStroke.model_validate(item) for item in record.strokes],
        )

    def _link_from_record(self, record: SessionRecord) -> CandidateLink:
        return CandidateLink(
            token=record.link_token or "",
            revokedAt=record.link_revoked_at,
            expiresAt=record.link_expires_at,
            maxUses=record.link_max_uses,
        )

    def _touch(self, record: SessionRecord) -> None:
        record.updated_at = now()

    def _id(self, prefix: str) -> str:
        return f"{prefix}-{uuid4().hex[:8]}"


store = InterviewStore()
