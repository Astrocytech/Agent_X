from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MvpCheckpoint:
    checkpoint_id: str
    run_id: str
    state_snapshot: dict
    created_at: str = ""
    hash: str = ""
    description: str = ""
    parent_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "run_id": self.run_id,
            "state_snapshot": self.state_snapshot,
            "created_at": self.created_at,
            "hash": self.hash,
            "description": self.description,
            "parent_id": self.parent_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> MvpCheckpoint:
        return cls(
            checkpoint_id=d["checkpoint_id"],
            run_id=d["run_id"],
            state_snapshot=d.get("state_snapshot", {}),
            created_at=d.get("created_at", ""),
            hash=d.get("hash", ""),
            description=d.get("description", ""),
            parent_id=d.get("parent_id"),
        )


def _compute_hash(snapshot: dict, timestamp: str) -> str:
    raw = json.dumps(snapshot, sort_keys=True) + timestamp
    return hashlib.sha256(raw.encode()).hexdigest()


class MvpCheckpointManager:
    def __init__(self, base_path: str | None = None) -> None:
        self._checkpoints: dict[str, MvpCheckpoint] = {}
        self._base_path = base_path
        if base_path:
            os.makedirs(base_path, exist_ok=True)

    def create_checkpoint(
        self,
        run_id: str,
        state_snapshot: dict,
        description: str = "",
        parent_id: str | None = None,
    ) -> MvpCheckpoint:
        created_at = datetime.now(timezone.utc).isoformat()
        raw_hash = _compute_hash(state_snapshot, created_at)
        checkpoint_id = hashlib.sha256(raw_hash.encode()).hexdigest()[:16]

        checkpoint = MvpCheckpoint(
            checkpoint_id=checkpoint_id,
            run_id=run_id,
            state_snapshot=state_snapshot,
            created_at=created_at,
            hash=raw_hash,
            description=description,
            parent_id=parent_id,
        )
        self._checkpoints[checkpoint_id] = checkpoint
        self._persist_checkpoint(checkpoint)
        return checkpoint

    def restore(self, checkpoint_id: str) -> dict | None:
        cp = self._checkpoints.get(checkpoint_id)
        if cp is None and self._base_path:
            cp = self._load_checkpoint(checkpoint_id)
        return cp.state_snapshot if cp else None

    def get_checkpoint(self, checkpoint_id: str) -> MvpCheckpoint | None:
        cp = self._checkpoints.get(checkpoint_id)
        if cp is None and self._base_path:
            cp = self._load_checkpoint(checkpoint_id)
        return cp

    def list_for_run(self, run_id: str) -> list[MvpCheckpoint]:
        results = [cp for cp in self._checkpoints.values() if cp.run_id == run_id]
        if self._base_path:
            results.extend(self._list_run_from_disk(run_id))
            seen = set()
            deduped = []
            for cp in results:
                if cp.checkpoint_id not in seen:
                    seen.add(cp.checkpoint_id)
                    deduped.append(cp)
            results = deduped
        return results

    def get_latest(self, run_id: str) -> MvpCheckpoint | None:
        run_cps = self.list_for_run(run_id)
        if not run_cps:
            return None
        run_cps.sort(key=lambda cp: cp.created_at, reverse=True)
        return run_cps[0]

    def validate(self, checkpoint_id: str) -> bool:
        cp = self._checkpoints.get(checkpoint_id)
        if cp is None and self._base_path:
            cp = self._load_checkpoint(checkpoint_id)
        if not cp:
            return False
        expected = _compute_hash(cp.state_snapshot, cp.created_at)
        return expected == cp.hash

    def branch(self, checkpoint_id: str, new_run_id: str) -> MvpCheckpoint | None:
        cp = self._checkpoints.get(checkpoint_id)
        if cp is None and self._base_path:
            cp = self._load_checkpoint(checkpoint_id)
        if not cp:
            return None
        return self.create_checkpoint(
            run_id=new_run_id,
            state_snapshot=cp.state_snapshot.copy(),
            description=f"Branch from {checkpoint_id}",
            parent_id=checkpoint_id,
        )

    def flush(self) -> None:
        if not self._base_path:
            return
        for cp in self._checkpoints.values():
            self._persist_checkpoint(cp)

    def _persist_checkpoint(self, checkpoint: MvpCheckpoint) -> None:
        if not self._base_path:
            return
        filepath = os.path.join(self._base_path, f"{checkpoint.checkpoint_id}.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(checkpoint.to_dict(), f, sort_keys=True)

    def _load_checkpoint(self, checkpoint_id: str) -> MvpCheckpoint | None:
        if not self._base_path:
            return None
        filepath = os.path.join(self._base_path, f"{checkpoint_id}.json")
        if not os.path.isfile(filepath):
            return None
        with open(filepath) as f:
            d = json.load(f)
        cp = MvpCheckpoint.from_dict(d)
        self._checkpoints[checkpoint_id] = cp
        return cp

    def _list_run_from_disk(self, run_id: str) -> list[MvpCheckpoint]:
        if not self._base_path:
            return []
        results: list[MvpCheckpoint] = []
        if not os.path.isdir(self._base_path):
            return results
        for fname in os.listdir(self._base_path):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(self._base_path, fname)
            try:
                with open(fpath) as f:
                    d = json.load(f)
                if d.get("run_id") == run_id:
                    cp = MvpCheckpoint.from_dict(d)
                    results.append(cp)
            except (json.JSONDecodeError, OSError, KeyError):
                continue
        return results
