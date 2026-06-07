from __future__ import annotations
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_CREATED = "CREATED"
STATE_PREFLIGHT_PASSED = "PREFLIGHT_PASSED"
STATE_CONTEXT_PACKED = "CONTEXT_PACKED"
STATE_MODEL_COMPLETED = "MODEL_COMPLETED"
STATE_PLAN_PARSED = "PLAN_PARSED"
STATE_PATCH_PROPOSED = "PATCH_PROPOSED"
STATE_PATCH_APPLIED = "PATCH_APPLIED"
STATE_VALIDATION_COMPLETED = "VALIDATION_COMPLETED"
STATE_EVIDENCE_WRITTEN = "EVIDENCE_WRITTEN"
STATE_PASS = "PASS"
STATE_FAIL = "FAIL"
STATE_BLOCKED = "BLOCKED"

ALL_STATES = [
    STATE_CREATED, STATE_PREFLIGHT_PASSED, STATE_CONTEXT_PACKED,
    STATE_MODEL_COMPLETED, STATE_PLAN_PARSED, STATE_PATCH_PROPOSED,
    STATE_PATCH_APPLIED, STATE_VALIDATION_COMPLETED, STATE_EVIDENCE_WRITTEN,
    STATE_PASS, STATE_FAIL, STATE_BLOCKED,
]

TERMINAL_STATES = {STATE_PASS, STATE_FAIL, STATE_BLOCKED}


class RunSession:
    def __init__(self, command: str, run_root: str = ".agentx-init/runs"):
        self.run_id = self._generate_run_id(command)
        self.run_dir = Path(run_root) / self.run_id
        self.command = command
        self.state = STATE_CREATED
        self._metadata: dict[str, Any] = {}

    @staticmethod
    def _generate_run_id(command: str) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        suffix = secrets.token_hex(4)
        return f"{ts}-{command}-{suffix}"

    def transition(self, new_state: str) -> None:
        if new_state not in ALL_STATES:
            raise ValueError(f"Invalid state: {new_state}")
        self.state = new_state

    def is_terminal(self) -> bool:
        return self.state in TERMINAL_STATES

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    def set_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value

    def ensure_run_dir(self) -> Path:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        return self.run_dir

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "command": self.command,
            "state": self.state,
            "metadata": self._metadata,
        }


class RunSessionManager:
    def __init__(self, run_root: str = ".agentx-init/runs"):
        self.run_root = run_root

    def create_session(self, command: str) -> RunSession:
        return RunSession(command=command, run_root=self.run_root)

    def list_runs(self) -> list[RunSession]:
        root = Path(self.run_root)
        if not root.exists():
            return []
        runs = []
        for entry in sorted(root.iterdir(), key=lambda p: p.stat().st_mtime):
            if entry.is_dir():
                run = RunSession(command="unknown", run_root=self.run_root)
                run.run_id = entry.name
                run.run_dir = entry
                runs.append(run)
        return runs
