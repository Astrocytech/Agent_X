import json
import os
from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    SCHEDULER_LEASE_STATUS_ACTIVE, SCHEDULER_LEASE_STATUS_RELEASED,
    SCHEDULER_LEASE_STATUS_EXPIRED, SCHEDULER_LEASE_STATUS_FAILED,
    SCHEDULER_LEASE_STATUS_VALUES,
    TaskClaim,
)


LEASE_HISTORY_FILE = "lease_history.jsonl"
CLAIM_HISTORY_FILE = "claim_history.jsonl"


class LeaseManager:
    def __init__(self, lease_dir: str | Path, lease_duration_seconds: int = 300):
        self.lease_dir = Path(lease_dir)
        self.lease_dir.mkdir(parents=True, exist_ok=True)
        self._lease_path = self.lease_dir / LEASE_HISTORY_FILE
        self._claim_path = self.lease_dir / CLAIM_HISTORY_FILE
        self._lease_duration = lease_duration_seconds
        self._append_counter = 0

    def _next_sequence(self) -> int:
        self._append_counter += 1
        return self._append_counter

    def create_lease(self, task_id: str, session_id: str) -> dict:
        active = self._get_active_leases()
        if task_id in active:
            return {"status": "LEASE_DENIED", "reason": "active_lease_exists", "task_id": task_id}
        now = utc_now_iso()
        lease_id = new_id("ls")
        from datetime import datetime, timezone, timedelta
        now_dt = datetime.now(timezone.utc)
        expires_dt = now_dt + timedelta(seconds=self._lease_duration)
        expires_at = expires_dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{expires_dt.microsecond:06d}Z"
        lease = {
            "lease_id": lease_id,
            "task_id": task_id,
            "session_id": session_id,
            "status": SCHEDULER_LEASE_STATUS_ACTIVE,
            "created_at": now,
            "expires_at": expires_at,
            "append_sequence": self._next_sequence(),
        }
        line = json.dumps(lease, sort_keys=True, default=str) + "\n"
        with open(self._lease_path, "a", encoding="utf-8") as f:
            f.write(line)
        claim_id = new_id("cl")
        claim = TaskClaim(
            claim_id=claim_id,
            task_id=task_id,
            session_id=session_id,
            lease_id=lease_id,
            expires_at=expires_at,
        )
        claim_line = json.dumps(to_dict(claim), sort_keys=True, default=str) + "\n"
        with open(self._claim_path, "a", encoding="utf-8") as f:
            f.write(claim_line)
        return {
            "status": "LEASE_ACQUIRED",
            "lease_id": lease_id,
            "claim_id": claim_id,
            "task_id": task_id,
            "session_id": session_id,
            "expires_at": expires_at,
        }

    def release_lease(self, lease_id: str, session_id: str) -> dict:
        leases = self._replay_leases()
        current = None
        for l in leases:
            if l.get("lease_id") == lease_id:
                current = l
        if current is None:
            return {"status": "LEASE_NOT_FOUND", "lease_id": lease_id}
        if current.get("session_id") != session_id:
            return {"status": "LEASE_NOT_OWNER", "lease_id": lease_id}
        now = utc_now_iso()
        release = dict(current)
        release["status"] = SCHEDULER_LEASE_STATUS_RELEASED
        release["released_at"] = now
        release["append_sequence"] = self._next_sequence()
        line = json.dumps(release, sort_keys=True, default=str) + "\n"
        with open(self._lease_path, "a", encoding="utf-8") as f:
            f.write(line)
        self._release_claim_for_lease(lease_id, now)
        return {"status": "LEASE_RELEASED", "lease_id": lease_id, "task_id": release.get("task_id")}

    def renew_lease(self, lease_id: str, session_id: str) -> dict:
        leases = self._replay_leases()
        current = None
        for l in leases:
            if l.get("lease_id") == lease_id:
                current = l
        if current is None:
            return {"status": "LEASE_NOT_FOUND", "lease_id": lease_id}
        if current.get("session_id") != session_id:
            return {"status": "LEASE_NOT_OWNER", "lease_id": lease_id}
        now = utc_now_iso()
        from datetime import datetime, timezone, timedelta
        now_dt = datetime.now(timezone.utc)
        expires_dt = now_dt + timedelta(seconds=self._lease_duration)
        expires_at = expires_dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{expires_dt.microsecond:06d}Z"
        renewed = dict(current)
        renewed["status"] = SCHEDULER_LEASE_STATUS_ACTIVE
        renewed["renewed_at"] = now
        renewed["expires_at"] = expires_at
        renewed["append_sequence"] = self._next_sequence()
        line = json.dumps(renewed, sort_keys=True, default=str) + "\n"
        with open(self._lease_path, "a", encoding="utf-8") as f:
            f.write(line)
        return {
            "status": "LEASE_RENEWED",
            "lease_id": lease_id,
            "expires_at": expires_at,
        }

    def get_active_lease(self, task_id: str) -> dict | None:
        active = self._get_active_leases()
        return active.get(task_id)

    def expire_stale_leases(self) -> list[dict]:
        leases = self._replay_leases()
        active = self._get_active_leases()
        expired = []
        now = utc_now_iso()
        for task_id, lease in active.items():
            if self._is_expired(lease):
                expired_entry = dict(lease)
                expired_entry["status"] = SCHEDULER_LEASE_STATUS_EXPIRED
                expired_entry["expired_at"] = now
                expired_entry["append_sequence"] = self._next_sequence()
                line = json.dumps(expired_entry, sort_keys=True, default=str) + "\n"
                with open(self._lease_path, "a", encoding="utf-8") as f:
                    f.write(line)
                expired.append(expired_entry)
        return expired

    def _get_active_leases(self) -> dict[str, dict]:
        leases = self._replay_leases()
        active: dict[str, dict] = {}
        for lease in leases:
            tid = lease.get("task_id", "")
            status = lease.get("status", "")
            if status == SCHEDULER_LEASE_STATUS_ACTIVE and not self._is_expired(lease):
                active[tid] = lease
            elif tid in active and status != SCHEDULER_LEASE_STATUS_ACTIVE:
                active.pop(tid, None)
        return active

    def _replay_leases(self) -> list[dict]:
        if not self._lease_path.exists():
            return []
        leases = []
        with open(self._lease_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    leases.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return leases

    def _is_expired(self, lease: dict) -> bool:
        expires_at = lease.get("expires_at", "")
        if not expires_at:
            return True
        try:
            from datetime import datetime, timezone
            expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return now > expires
        except (ValueError, TypeError):
            return True

    def _release_claim_for_lease(self, lease_id: str, now: str) -> None:
        if not self._claim_path.exists():
            return
        claims = []
        with open(self._claim_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    claims.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        latest_claim = None
        for c in claims:
            if c.get("lease_id") == lease_id:
                latest_claim = c
        if latest_claim:
            release = dict(latest_claim)
            release["claim_status"] = "RELEASED"
            release["released_at"] = now
            release_line = json.dumps(release, sort_keys=True, default=str) + "\n"
            with open(self._claim_path, "a", encoding="utf-8") as f:
                f.write(release_line)
