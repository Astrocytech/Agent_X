from __future__ import annotations
from pathlib import Path
from agentx_evolve.patch.patch_models import PatchAction, sha256_file, utc_now_iso
from agentx_evolve.security.safe_file_ops import safe_exact_edit, safe_write_file
from agentx_evolve.security.sandbox_policy import SandboxPolicy
from agentx_evolve.security.security_models import (
    STATUS_SUCCESS, STATUS_BLOCKED, OP_EDIT, OP_WRITE,
    SandboxDecision, DECISION_ALLOW, DECISION_BLOCK,
)


class PatchApplier:
    def __init__(
        self,
        repo_root: Path,
        policy: SandboxPolicy,
        implementation_session_id: str,
        governance_decision_id: str,
    ):
        self._repo_root = repo_root.resolve()
        self._policy = policy
        self._session_id = implementation_session_id
        self._gov_id = governance_decision_id

    def apply_action(self, action: PatchAction) -> PatchAction:
        if action.change_type == "UPDATE":
            return self._apply_update(action)
        elif action.change_type == "CREATE":
            return self._apply_create(action)
        elif action.change_type == "DELETE":
            return self._apply_delete(action)
        else:
            action.status = "FAILED"
            action.errors.append(f"Unknown change type: {action.change_type}")
            return action

    def _apply_update(self, action: PatchAction) -> PatchAction:
        action.timestamp = utc_now_iso()
        action.status = "APPLYING"

        if not action.old_text:
            action.status = "FAILED"
            action.errors.append("UPDATE action requires old_text")
            return action

        full_path = self._repo_root / action.target_file
        if full_path.exists():
            action.old_hash = sha256_file(full_path)

        result = safe_exact_edit(
            action.target_file,
            action.old_text,
            action.new_text,
            self._repo_root,
            self._policy,
            implementation_session_id=self._session_id,
            governance_decision_id=self._gov_id,
        )

        if result.status == STATUS_SUCCESS:
            action.status = "APPLIED"
            action.old_hash = result.before_hash
            action.new_hash = result.after_hash
            action.warnings.extend(result.warnings)
        else:
            action.status = "FAILED"
            action.errors.extend(result.errors)

        return action

    def _apply_create(self, action: PatchAction) -> PatchAction:
        action.timestamp = utc_now_iso()
        action.status = "APPLYING"

        result = safe_write_file(
            action.target_file,
            action.new_text,
            self._repo_root,
            self._policy,
            implementation_session_id=self._session_id,
            governance_decision_id=self._gov_id,
        )

        if result.status == STATUS_SUCCESS:
            action.status = "APPLIED"
            action.new_hash = result.after_hash
            action.warnings.extend(result.warnings)
        else:
            action.status = "FAILED"
            action.errors.extend(result.errors)

        return action

    def _apply_delete(self, action: PatchAction) -> PatchAction:
        action.timestamp = utc_now_iso()
        full_path = (self._repo_root / action.target_file).resolve()
        if not full_path.exists():
            action.status = "FAILED"
            action.errors.append(f"File not found for deletion: {action.target_file}")
            return action

        try:
            full_path.unlink()
            action.status = "APPLIED"
            action.old_hash = action.old_hash or ""
        except OSError as e:
            action.status = "FAILED"
            action.errors.append(f"Delete error: {e}")

        return action
