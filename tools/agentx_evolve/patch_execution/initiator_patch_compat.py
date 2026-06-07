from __future__ import annotations

import json
from pathlib import Path

from agentx_evolve.patch_execution.patch_models import utc_now_iso


class InitiatorPatchCompat:
    def __init__(self, repo_root: Path | None = None) -> None:
        self._repo_root: Path | None = repo_root

    def get_repo_root(self) -> Path:
        if self._repo_root is not None:
            return self._repo_root
        return Path(".")

    def get_runtime_state_root(self) -> Path:
        return self.get_repo_root() / ".agentx-init"

    def load_proposal(self, proposal_id: str) -> dict:
        raise NotImplementedError("Initiator integration required to load proposals")

    def load_governance_decision(self, governance_decision_id: str) -> dict:
        raise NotImplementedError("Initiator integration required to load governance decisions")

    def validate_schema(self, artifact: dict, schema_id: str) -> dict:
        raise NotImplementedError("Initiator integration required for schema validation")

    def write_json_atomic(self, path: Path, artifact: dict) -> dict:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(artifact, indent=2, default=str), encoding="utf-8")
            tmp.rename(path)
            return {"success": True, "path": str(path)}
        except OSError as e:
            return {"success": False, "error": str(e)}

    def append_jsonl(self, path: Path, artifact: dict) -> dict:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(artifact, default=str) + "\n")
            return {"success": True, "path": str(path)}
        except OSError as e:
            return {"success": False, "error": str(e)}

    def append_audit_event(self, event: dict) -> dict:
        path = self.get_runtime_state_root() / "memory" / "audit_events.jsonl"
        return self.append_jsonl(path, event)

    def run_validation_command(self, command: list[str]) -> dict:
        raise NotImplementedError("Initiator integration required for validation commands")
