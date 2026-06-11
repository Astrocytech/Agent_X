from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MvpStateStore:
    def __init__(self, root: str | Path):
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def _run_path(self, run_id: str) -> Path:
        return self._root / f"run_{run_id}.jsonl"

    def _goal_path(self, goal_id: str) -> Path:
        return self._root / f"goal_{goal_id}.jsonl"

    def _action_path(self, action_id: str) -> Path:
        return self._root / f"action_{action_id}.jsonl"

    def _append(self, path: Path, record: dict) -> None:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def create_record(self, record_type: str, record_id: str,
                      run_id: str, data: dict) -> dict:
        record = {
            "record_type": record_type,
            "record_id": record_id,
            "run_id": run_id,
            "data": data,
        }
        self._append(self._run_path(run_id), record)
        return record

    def read_records(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        records = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def query_by_run(self, run_id: str) -> list[dict]:
        return self.read_records(self._run_path(run_id))

    def query_by_goal(self, goal_id: str) -> list[dict]:
        return self.read_records(self._goal_path(goal_id))

    def query_by_action(self, action_id: str) -> list[dict]:
        return self.read_records(self._action_path(action_id))

    def update_through_transition(self, run_id: str, record_id: str,
                                  new_data: dict) -> bool:
        path = self._run_path(run_id)
        if not path.exists():
            return False
        lines = path.read_text(encoding="utf-8").splitlines()
        updated = False
        out_lines = []
        for line in lines:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("record_id") == record_id:
                rec["data"].update(new_data)
                updated = True
            out_lines.append(json.dumps(rec))
        if updated:
            path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
        return updated

    def append_event(self, run_id: str, event: dict) -> dict:
        path = self._run_path(run_id)
        record = {"record_type": "event", "event": event}
        self._append(path, record)
        return record

    def snapshot(self, run_id: str) -> dict | None:
        records = self.query_by_run(run_id)
        if not records:
            return None
        return {"run_id": run_id, "record_count": len(records), "records": records}

    def restore(self, snapshot: dict) -> bool:
        run_id = snapshot.get("run_id", "")
        if not run_id:
            return False
        path = self._run_path(run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        records = snapshot.get("records", [])
        with path.open("w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")
        return True

    def validate_integrity(self, run_id: str) -> list[str]:
        issues = []
        path = self._run_path(run_id)
        if not path.exists():
            return ["No records found"]
        records = self.read_records(path)
        if not records:
            return ["Empty record set"]
        for i, rec in enumerate(records):
            if "record_type" not in rec:
                issues.append(f"Record {i}: missing record_type")
            if "record_id" not in rec:
                issues.append(f"Record {i}: missing record_id")
        return issues
