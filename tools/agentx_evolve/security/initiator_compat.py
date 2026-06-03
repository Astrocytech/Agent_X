from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

_INITIATOR_IMPORT_ERRORS: list[str] = []

try:
    from agentx_initiator.core import path_registry as _path_registry
except ImportError as e:
    _INITIATOR_IMPORT_ERRORS.append(f"path_registry: {e}")
    _path_registry = None

try:
    from agentx_initiator.core import source_guard as _source_guard
except ImportError as e:
    _INITIATOR_IMPORT_ERRORS.append(f"source_guard: {e}")
    _source_guard = None

try:
    from agentx_initiator.core import schema_validation as _schema_validation
except ImportError as e:
    _INITIATOR_IMPORT_ERRORS.append(f"schema_validation: {e}")
    _schema_validation = None

try:
    from agentx_initiator.core import artifact_io as _artifact_io
except ImportError as e:
    _INITIATOR_IMPORT_ERRORS.append(f"artifact_io: {e}")
    _artifact_io = None

try:
    from agentx_initiator.core import audit_log as _audit_log
except ImportError as e:
    _INITIATOR_IMPORT_ERRORS.append(f"audit_log: {e}")
    _audit_log = None


class InitiatorCompat:
    def __init__(self, repo_root: Path | None = None):
        self._repo_root = repo_root
        self._integration_failures: list[str] = list(_INITIATOR_IMPORT_ERRORS)

    @property
    def integration_failures(self) -> list[str]:
        return list(self._integration_failures)

    def get_repo_root(self) -> Path:
        if _path_registry is not None:
            try:
                return _path_registry.repo_root()
            except Exception:
                pass
        if self._repo_root:
            return self._repo_root
        return Path.cwd()

    def get_runtime_state_root(self) -> Path:
        if _path_registry is not None:
            try:
                return _path_registry.state_dir()
            except Exception:
                pass
        return self.get_repo_root() / ".agentx-init"

    def get_protected_paths(self) -> list[str]:
        return ["L0/", "agent_x/runtime/", "core/"]

    def check_source_guard(self, target_paths: list[str]) -> dict:
        """Partial stub: captures source state via Initiator but does not
        enforce an approved-mutation policy. Full enforcement requires
        Initiator's SourceGuard to be running with a mutation allowlist."""
        if _source_guard is not None:
            try:
                root = self.get_repo_root()
                before = _source_guard.capture_source_state(root)
                return {
                    "integration": "initiator_source_guard",
                    "before_state_captured": True,
                    "paths_checked": target_paths,
                    "validation_note": "intro_only_no_mutation_policy",
                }
            except Exception as e:
                self._integration_failures.append(f"source_guard.check: {e}")
        return {
            "integration": "fallback",
            "before_state_captured": False,
            "paths_checked": target_paths,
            "warning": "Source guard check unavailable",
        }

    def validate_schema(self, artifact: dict, schema_id: str) -> dict:
        if _schema_validation is not None:
            try:
                result = _schema_validation.validate_instance(artifact, schema_id)
                return {
                    "valid": result.valid,
                    "errors": result.errors,
                    "integration": "initiator_schema_validation",
                }
            except Exception as e:
                self._integration_failures.append(f"schema_validation.validate: {e}")
        return {
            "valid": False,
            "errors": ["Schema validation unavailable — failing closed"],
            "integration": "fallback",
            "warning": "Schema validation unavailable — failing closed",
        }

    def write_json_atomic(self, path: Path, artifact: dict) -> dict:
        if _artifact_io is not None:
            try:
                schema_name = artifact.get("schema_id", "unknown")
                result = _artifact_io.write_validated_latest(path, artifact, schema_name)
                return {
                    "status": result.status,
                    "path": str(result.path) if result.path else None,
                    "error": result.error,
                    "integration": "initiator_artifact_io",
                }
            except Exception as e:
                self._integration_failures.append(f"artifact_io.write: {e}")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(f".tmp.{uuid4().hex}")
            tmp.write_text(json.dumps(artifact, indent=2, default=str))
            tmp.replace(path)
            return {"status": "SUCCESS", "path": str(path), "integration": "fallback"}
        except OSError as e:
            return {"status": "FAILED", "error": str(e), "integration": "fallback"}

    def append_audit_event(self, event: dict) -> dict:
        if _audit_log is not None:
            try:
                result = _audit_log.append_event(event)
                return {
                    "status": result.status,
                    "event_id": result.event_id,
                    "integration": "initiator_audit_log",
                }
            except Exception as e:
                self._integration_failures.append(f"audit_log.append: {e}")
        try:
            path = self.get_runtime_state_root() / "memory" / "audit_events.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a") as f:
                f.write(json.dumps(event, separators=(",", ":")) + "\n")
            return {
                "status": "SUCCESS",
                "event_id": event.get("event_id", str(uuid4())),
                "integration": "fallback",
            }
        except OSError as e:
            return {"status": "FAILED", "error": str(e), "integration": "fallback"}
