from __future__ import annotations
import json
import importlib
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from agentx_evolve.patch_execution.patch_models import MutationAllowlist

_INITIATOR_IMPORT_ERRORS: list[str] = []

_INITIATOR_MODULES: list[tuple[str, str]] = [
    ("agentx_initiator.core.path_registry", "path_registry"),
    ("agentx_initiator.core.source_guard", "source_guard"),
    ("agentx_initiator.core.schema_validation", "schema_validation"),
    ("agentx_initiator.core.artifact_io", "artifact_io"),
    ("agentx_initiator.core.audit_log", "audit_log"),
]

def _try_imports() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for full_name, short_name in _INITIATOR_MODULES:
        try:
            mod = importlib.import_module(full_name)
            result[short_name] = mod
        except ImportError as e:
            err = f"{short_name}: {e}"
            if err not in _INITIATOR_IMPORT_ERRORS:
                _INITIATOR_IMPORT_ERRORS.append(err)
            result[short_name] = None
    return result

_first_imports = _try_imports()


class InitiatorCompat:
    def __init__(self, repo_root: Path | None = None):
        self._repo_root = repo_root
        self._integration_failures: list[str] = list(_INITIATOR_IMPORT_ERRORS)
        self._modules = dict(_first_imports)
        self._degraded = self._modules.get("path_registry") is None and repo_root is None

    @property
    def integration_failures(self) -> list[str]:
        return list(self._integration_failures)

    @property
    def degraded(self) -> bool:
        return self._degraded

    def refresh_integration_status(self):
        self._modules = _try_imports()
        self._integration_failures = list(_INITIATOR_IMPORT_ERRORS)
        self._degraded = self._modules.get("path_registry") is None and self._repo_root is None

    def get_repo_root(self) -> Path:
        p_reg = self._modules.get("path_registry")
        if p_reg is not None:
            try:
                return p_reg.repo_root()
            except Exception:
                pass
        if self._repo_root:
            return self._repo_root
        self._degraded = True
        raise RuntimeError(
            "Initiator path_registry unavailable and no repo_root provided — "
            "cannot determine repository root in safety-critical context"
        )

    def get_runtime_state_root(self) -> Path:
        p_reg = self._modules.get("path_registry")
        if p_reg is not None:
            try:
                return p_reg.state_dir()
            except Exception:
                pass
        root = self.get_repo_root()
        return root / ".agentx-init"

    def get_protected_paths(self) -> list[str]:
        return ["L0/", "agent_x/runtime/", "core/"]

    def check_source_guard(
        self,
        target_paths: list[str],
        mutation_allowlist: MutationAllowlist | None = None,
    ) -> dict:
        if mutation_allowlist is not None and not mutation_allowlist.is_empty():
            unapproved: list[str] = []
            for tp in target_paths:
                if not mutation_allowlist.allows_mutation(tp, "UPDATE") and not mutation_allowlist.allows_mutation(tp, "CREATE"):
                    unapproved.append(tp)
            if unapproved:
                return {
                    "integration": "mutation_allowlist",
                    "before_state_captured": False,
                    "paths_checked": target_paths,
                    "enforces_approved_mutation_scope": True,
                    "approved": False,
                    "unapproved_paths": unapproved,
                    "validation_note": "mutation_not_in_allowlist",
                }
            return {
                "integration": "mutation_allowlist",
                "before_state_captured": True,
                "paths_checked": target_paths,
                "enforces_approved_mutation_scope": True,
                "approved": True,
                "validation_note": "all_mutations_approved",
            }

        s_guard = self._modules.get("source_guard")
        if s_guard is not None:
            try:
                root = self.get_repo_root()
                before = s_guard.capture_source_state(root)
                return {
                    "integration": "initiator_source_guard",
                    "before_state_captured": True,
                    "paths_checked": target_paths,
                    "enforces_approved_mutation_scope": False,
                    "validation_note": "intro_only_no_mutation_policy",
                }
            except (RuntimeError, Exception) as e:
                self._integration_failures.append(f"source_guard.check: {e}")
        return {
            "integration": "fallback",
            "before_state_captured": False,
            "paths_checked": target_paths,
            "enforces_approved_mutation_scope": False,
            "warning": "Source guard check unavailable",
        }

    def validate_schema(self, artifact: dict, schema_id: str) -> dict:
        s_val = self._modules.get("schema_validation")
        if s_val is not None:
            try:
                result = s_val.validate_instance(artifact, schema_id)
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
        a_io = self._modules.get("artifact_io")
        if a_io is not None:
            try:
                schema_name = artifact.get("schema_id", "unknown")
                result = a_io.write_validated_latest(path, artifact, schema_name)
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
        a_log = self._modules.get("audit_log")
        if a_log is not None:
            try:
                result = a_log.append_event(event)
                return {
                    "status": result.status,
                    "event_id": result.event_id,
                    "integration": "initiator_audit_log",
                }
            except Exception as e:
                self._integration_failures.append(f"audit_log.append: {e}")
        try:
            runtime = self.get_runtime_state_root()
        except RuntimeError as e:
            return {"status": "FAILED", "error": str(e), "integration": "fallback"}
        try:
            path = runtime / "memory" / "audit_events.jsonl"
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
