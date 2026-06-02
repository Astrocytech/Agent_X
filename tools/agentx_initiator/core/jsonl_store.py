from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class JsonlAppendResult:
    status: str = "SUCCESS"
    line_count: int = 0
    error: Optional[str] = None
    warning: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "line_count": self.line_count,
            "error": self.error,
            "warning": self.warning,
        }


def append_jsonl(path: Path, record: dict) -> JsonlAppendResult:
    path = path.resolve()
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.touch()

    try:
        with open(path, "a") as f:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")
    except OSError as e:
        return JsonlAppendResult(status="FAILED", error=str(e))

    line_count = 0
    try:
        with open(path) as f:
            for _ in f:
                line_count += 1
    except OSError:
        pass

    return JsonlAppendResult(status="SUCCESS", line_count=line_count)


def read_jsonl(path: Path, limit: int = 0) -> list[dict]:
    path = path.resolve()
    if not path.exists():
        return []
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    if limit > 0:
        return records[-limit:]
    return records
