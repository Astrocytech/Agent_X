from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


_RECORD_TYPES = frozenset({
    "goal_state", "plan_draft", "candidate_action",
    "simulation_result", "validation_result",
    "observation", "critique", "question",
})


@dataclass
class MvpBlackboardRecord:
    record_id: str
    record_type: str
    owner: str
    run_id: str
    data: dict
    version: int = 1
    created_at: str = ""
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "record_type": self.record_type,
            "owner": self.owner,
            "run_id": self.run_id,
            "data": self.data,
            "version": self.version,
            "created_at": self.created_at,
            "evidence_refs": list(self.evidence_refs),
        }

    @classmethod
    def from_dict(cls, d: dict) -> MvpBlackboardRecord:
        return cls(
            record_id=d["record_id"],
            record_type=d["record_type"],
            owner=d["owner"],
            run_id=d["run_id"],
            data=d.get("data", {}),
            version=d.get("version", 1),
            created_at=d.get("created_at", ""),
            evidence_refs=d.get("evidence_refs", []),
        )


class MvpBlackboard:
    def __init__(self, base_path: str | None = None) -> None:
        self._records: dict[str, MvpBlackboardRecord] = {}
        self._base_path = base_path
        if base_path:
            os.makedirs(base_path, exist_ok=True)

    def write(self, record: MvpBlackboardRecord) -> MvpBlackboardRecord:
        existing = self._records.get(record.record_id)
        version = existing.version + 1 if existing else 1
        record.version = version
        if not record.created_at:
            record.created_at = datetime.now(timezone.utc).isoformat()
        self._records[record.record_id] = record
        self._persist_record(record)
        return record

    def read(self, record_id: str) -> MvpBlackboardRecord | None:
        return self._records.get(record_id)

    def query(
        self,
        run_id: str = "",
        record_type: str = "",
        owner: str = "",
    ) -> list[MvpBlackboardRecord]:
        results = list(self._records.values())
        if run_id:
            results = [r for r in results if r.run_id == run_id]
        if record_type:
            results = [r for r in results if r.record_type == record_type]
        if owner:
            results = [r for r in results if r.owner == owner]
        return results

    def search_data(self, run_id: str, key: str, value: Any) -> list[MvpBlackboardRecord]:
        candidates = self.query(run_id=run_id) if run_id else list(self._records.values())
        return [r for r in candidates if r.data.get(key) == value]

    def get_latest(self, record_type: str, run_id: str) -> MvpBlackboardRecord | None:
        candidates = [
            r for r in self._records.values()
            if r.record_type == record_type and r.run_id == run_id
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda r: r.created_at)

    def list_by_owner(self, owner: str) -> list[MvpBlackboardRecord]:
        return [r for r in self._records.values() if r.owner == owner]

    def list_by_run(self, run_id: str) -> list[MvpBlackboardRecord]:
        return [r for r in self._records.values() if r.run_id == run_id]

    def load_run(self, run_id: str) -> None:
        if not self._base_path:
            return
        filepath = os.path.join(self._base_path, f"{run_id}.jsonl")
        if not os.path.isfile(filepath):
            return
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    record = MvpBlackboardRecord.from_dict(d)
                    self._records[record.record_id] = record
                except (json.JSONDecodeError, KeyError):
                    continue

    def flush(self) -> None:
        if not self._base_path:
            return
        for run_id in {r.run_id for r in self._records.values()}:
            self._flush_run(run_id)

    def _persist_record(self, record: MvpBlackboardRecord) -> None:
        if not self._base_path:
            return
        filepath = os.path.join(self._base_path, f"{record.run_id}.jsonl")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "a") as f:
            f.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    def _flush_run(self, run_id: str) -> None:
        if not self._base_path:
            return
        filepath = os.path.join(self._base_path, f"{run_id}.jsonl")
        records = [r for r in self._records.values() if r.run_id == run_id]
        records.sort(key=lambda r: r.created_at)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            for record in records:
                f.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")
