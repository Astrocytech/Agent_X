import json
from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict, compute_session_record_hash,
    SessionRecord,
    SCHEDULER_SESSION_STATUS_ACTIVE, SCHEDULER_SESSION_STATUS_HEARTBEAT,
    SCHEDULER_SESSION_STATUS_CLOSED, SCHEDULER_SESSION_STATUS_STALE,
    SCHEDULER_SESSION_STATUS_FAILED,
    SCHEDULER_ACTIVE_SESSION_STATUSES,
    SCHEDULER_SESSION_STATUS_VALUES,
)


SESSION_HISTORY_FILE = "session_history.jsonl"
SESSION_SNAPSHOT_FILE = "session_state.json"
SESSION_LOCK_FILE = "session.lock"


class SessionStore:
    def __init__(self, session_dir: str | Path):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self._history_path = self.session_dir / SESSION_HISTORY_FILE
        self._snapshot_path = self.session_dir / SESSION_SNAPSHOT_FILE
        self._lock_path = self.session_dir / SESSION_LOCK_FILE
        self._append_counter = 0

    def _next_sequence(self) -> int:
        self._append_counter += 1
        return self._append_counter

    def append_session(self, session: SessionRecord) -> dict:
        record = to_dict(session)
        record["session_record_hash"] = compute_session_record_hash(record)
        line = json.dumps(record, sort_keys=True, default=str) + "\n"
        with open(self._history_path, "a", encoding="utf-8") as f:
            f.write(line)
        return {"record_id": session.record_id, "session_id": session.session_id, "status": "appended"}

    def replay_sessions(self) -> list[SessionRecord]:
        sessions = []
        if not self._history_path.exists():
            return sessions
        with open(self._history_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                record = self._dict_to_session_record(data)
                if record is not None:
                    sessions.append(record)
        return sessions

    def get_effective_sessions(self) -> dict[str, SessionRecord]:
        sessions = self.replay_sessions()
        effective: dict[str, SessionRecord] = {}
        for s in sorted(sessions, key=lambda x: (x.append_sequence, x.updated_at or "", x.record_id)):
            effective[s.session_id] = s
        return effective

    def get_active_sessions(self) -> list[SessionRecord]:
        effective = self.get_effective_sessions()
        return [s for s in effective.values() if s.status in SCHEDULER_ACTIVE_SESSION_STATUSES]

    def close_session(self, session_id: str, role: str = "default") -> SessionRecord | None:
        effective = self.get_effective_sessions()
        current = effective.get(session_id)
        now = utc_now_iso()
        record_id = new_id("srec")
        session = SessionRecord(
            record_id=record_id,
            session_id=session_id,
            role=role or "default",
            status=SCHEDULER_SESSION_STATUS_CLOSED,
            closed_at=now,
            created_at=current.created_at if current else now,
            updated_at=now,
            append_sequence=self._next_sequence(),
            revision=(current.revision + 1) if current else 1,
            previous_record_hash=current.session_record_hash if current else "",
        )
        self.append_session(session)
        return session

    def heartbeat_session(self, session_id: str, role: str = "default") -> SessionRecord | None:
        effective = self.get_effective_sessions()
        current = effective.get(session_id)
        now = utc_now_iso()
        if current is None:
            return None
        record_id = new_id("srec")
        session = SessionRecord(
            record_id=record_id,
            session_id=session_id,
            role=role or current.role,
            status=SCHEDULER_SESSION_STATUS_HEARTBEAT,
            heartbeat_at=now,
            created_at=current.created_at,
            updated_at=now,
            closed_at=current.closed_at,
            append_sequence=self._next_sequence(),
            revision=current.revision + 1,
            previous_record_hash=current.session_record_hash,
        )
        self.append_session(session)
        return session

    def mark_stale(self, session_id: str, role: str = "default") -> SessionRecord | None:
        effective = self.get_effective_sessions()
        current = effective.get(session_id)
        if current is None:
            return None
        now = utc_now_iso()
        record_id = new_id("srec")
        session = SessionRecord(
            record_id=record_id,
            session_id=session_id,
            role=role or current.role,
            status=SCHEDULER_SESSION_STATUS_STALE,
            created_at=current.created_at,
            updated_at=now,
            closed_at=now,
            append_sequence=self._next_sequence(),
            revision=current.revision + 1,
            previous_record_hash=current.session_record_hash,
        )
        self.append_session(session)
        return session

    def _dict_to_session_record(self, data: dict) -> SessionRecord | None:
        try:
            return SessionRecord(
                record_id=data.get("record_id", ""),
                session_id=data.get("session_id", ""),
                role=data.get("role", "default"),
                status=data.get("status", SCHEDULER_SESSION_STATUS_ACTIVE),
                heartbeat_at=data.get("heartbeat_at"),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
                closed_at=data.get("closed_at"),
                previous_record_hash=data.get("previous_record_hash", ""),
                session_record_hash=data.get("session_record_hash", ""),
                append_sequence=data.get("append_sequence", 0),
                revision=data.get("revision", 1),
                warnings=data.get("warnings", []),
                errors=data.get("errors", []),
            )
        except (KeyError, TypeError):
            return None
