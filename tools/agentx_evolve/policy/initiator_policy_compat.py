from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .policy_models import PolicyDecision

_INITIATOR_AVAILABLE = False
_INITIATOR_ERROR = "INITIATOR_POLICY_INTEGRATION_FAILED"

try:
    from agentx_initiator.core import schema_validation
    from agentx_initiator.core import artifact_io
    from agentx_initiator.core import audit_log
    from agentx_initiator.core import path_registry
    _INITIATOR_AVAILABLE = all(
        hasattr(m, f)
        for m, f in [
            (schema_validation, "validate_schema"),
            (artifact_io, "write_json_atomic"),
            (audit_log, "append_audit_event"),
        ]
    )
except ImportError:
    pass


class InitiatorPolicyCompat:
    def __init__(self, repo_root: Path | None = None) -> None:
        self._repo_root = repo_root or Path.cwd()
        self._policy_root = self._repo_root / ".agentx-init" / "policies"

    def get_repo_root(self) -> Path:
        return self._repo_root

    def get_policy_runtime_root(self) -> Path:
        return self._policy_root

    def validate_schema(self, artifact: dict, schema_id: str) -> dict:
        if _INITIATOR_AVAILABLE:
            return schema_validation.validate_schema(artifact, schema_id)
        return {"success": False, "error": _INITIATOR_ERROR, "schema_id": schema_id}

    def write_json_atomic(self, path: Path, artifact: dict) -> dict:
        if _INITIATOR_AVAILABLE:
            return artifact_io.write_json_atomic(path, artifact)
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(".tmp")
            with open(tmp, "w") as f:
                json.dump(artifact, f, indent=2)
                f.flush()
            tmp.replace(p)
            return {"success": True, "path": str(p)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def append_audit_event(self, event: dict) -> dict:
        if _INITIATOR_AVAILABLE:
            return audit_log.append_audit_event(event)
        try:
            path = self._policy_root / "policy_decisions.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a") as f:
                f.write(json.dumps(event) + "\n")
            return {"success": True, "path": str(path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def append_policy_decision(self, decision: PolicyDecision) -> dict:
        try:
            return self.append_audit_event(decision.to_dict())
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_latest_policy_decision(self, decision: PolicyDecision) -> dict:
        try:
            path = self._policy_root / "latest_policy_decision.json"
            return self.write_json_atomic(path, decision.to_dict())
        except Exception as e:
            return {"success": False, "error": str(e)}


import logging

def get_policy_registry(*args: Any, **kwargs: Any) -> Any | None:
    try:
        from .policy_registry import PolicyRegistry
        return PolicyRegistry(*args, **kwargs)
    except Exception as e:
        logging.getLogger(__name__).warning("PolicyRegistry construction failed: %s", e)
        return None
