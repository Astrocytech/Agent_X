from __future__ import annotations
import json
from pathlib import Path
from agentx_evolve.failure.failure_models import (
    FailureEvent, FailureReport, to_dict, new_id, utc_now_iso,
)


class FailureEvidenceWriter:
    def __init__(self, repo_root: Path):
        self._repo_root = repo_root.resolve()
        self._failure_dir = self._repo_root / ".agentx-init" / "failures"

    def write_event(self, event: FailureEvent) -> dict:
        path = self._failure_dir / "failure_events.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(event.to_dict(), separators=(",", ":")) + "\n")
        return {"status": "APPENDED", "path": str(path)}

    def write_report(self, report: FailureReport) -> dict:
        path = self._failure_dir / "failure_reports.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(report.to_dict(), separators=(",", ":")) + "\n")
        return {"status": "APPENDED", "path": str(path)}

    def write_latest_events(self, events: list[FailureEvent]) -> dict:
        path = self._failure_dir / "failure_latest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".tmp.{new_id()}")
        tmp.write_text(
            json.dumps(
                {"events": [e.to_dict() for e in events]},
                indent=2, default=str,
            )
        )
        tmp.replace(path)
        return {"status": "WRITTEN", "path": str(path)}

    def get_event_log_path(self) -> Path:
        return self._failure_dir / "failure_events.jsonl"

    def get_report_log_path(self) -> Path:
        return self._failure_dir / "failure_reports.jsonl"

    def get_latest_path(self) -> Path:
        return self._failure_dir / "failure_latest.json"
