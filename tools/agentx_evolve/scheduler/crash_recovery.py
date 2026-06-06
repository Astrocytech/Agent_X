import json
from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    SCHEDULER_EVENT_RECOVERED,
    SCHEDULER_SESSION_STATUS_STALE, SCHEDULER_SESSION_STATUS_FAILED,
    SCHEDULER_LEASE_STATUS_EXPIRED,
    SCHEDULER_LOCK_STATUS_STALE,
    SessionRecord,
)


RECOVERY_EVENT_FILE = "recovery_events.jsonl"


class CrashRecovery:
    def __init__(self, recovery_dir: str | Path):
        self.recovery_dir = Path(recovery_dir)
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        self._event_path = self.recovery_dir / RECOVERY_EVENT_FILE

    def recover_stale_sessions(self, sessions: list[SessionRecord]) -> list[dict]:
        from datetime import datetime, timezone
        recovered = []
        now = datetime.now(timezone.utc)
        for session in sessions:
            if session.status not in ("ACTIVE", "HEARTBEAT"):
                continue
            hb = session.heartbeat_at or session.updated_at
            if not hb:
                continue
            try:
                hb_time = datetime.fromisoformat(hb.replace("Z", "+00:00"))
                elapsed = (now - hb_time).total_seconds()
            except (ValueError, TypeError):
                continue
            if elapsed > 600:
                event = {
                    "recovery_id": new_id("rcv"),
                    "session_id": session.session_id,
                    "recovery_type": "stale_session",
                    "previous_status": session.status,
                    "new_status": SCHEDULER_SESSION_STATUS_STALE,
                    "recovered_at": utc_now_iso(),
                    "elapsed_seconds": elapsed,
                }
                self._write_recovery_event(event)
                recovered.append(event)
        return recovered

    def recover_expired_leases(self, expired_leases: list[dict]) -> list[dict]:
        recovered = []
        for lease in expired_leases:
            event = {
                "recovery_id": new_id("rcv"),
                "lease_id": lease.get("lease_id", ""),
                "task_id": lease.get("task_id", ""),
                "session_id": lease.get("session_id", ""),
                "recovery_type": "expired_lease",
                "previous_status": lease.get("status", "ACTIVE"),
                "new_status": SCHEDULER_LEASE_STATUS_EXPIRED,
                "recovered_at": utc_now_iso(),
            }
            self._write_recovery_event(event)
            recovered.append(event)
        return recovered

    def recover_stale_locks(self, lock_dir: Path) -> list[dict]:
        recovered = []
        for lock_file in lock_dir.glob("*.lock"):
            if not lock_file.is_file():
                continue
            recovery_file = lock_file.with_suffix(".recovery.json")
            if recovery_file.exists():
                continue
            try:
                with open(lock_file, "r", encoding="utf-8") as f:
                    lock_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            event = {
                "recovery_id": new_id("rcv"),
                "lock_name": lock_file.stem,
                "owner_id": lock_data.get("owner_id", ""),
                "recovery_type": "stale_lock",
                "previous_status": lock_data.get("status", "ACTIVE"),
                "new_status": SCHEDULER_LOCK_STATUS_STALE,
                "recovered_at": utc_now_iso(),
            }
            self._write_recovery_event(event)
            recovery_data = {
                "lock_name": lock_file.stem,
                "previous_owner": lock_data.get("owner_id", ""),
                "new_owner": "recovery",
                "status": SCHEDULER_LOCK_STATUS_STALE,
                "recovered_at": utc_now_iso(),
            }
            with open(recovery_file, "w", encoding="utf-8") as f:
                json.dump(recovery_data, f, indent=2, default=str)
            lock_file.unlink(missing_ok=True)
            recovered.append(event)
        return recovered

    def _write_recovery_event(self, event: dict) -> None:
        line = json.dumps(event, sort_keys=True, default=str) + "\n"
        with open(self._event_path, "a", encoding="utf-8") as f:
            f.write(line)
