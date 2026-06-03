from __future__ import annotations
from pathlib import Path
from agentx_evolve.security.path_boundary import check_path_boundary
from agentx_evolve.security.sandbox_policy import is_l0_path, is_protected_path
from agentx_evolve.security.security_models import (
    SandboxPolicy, SandboxDecision, DECISION_ALLOW, DECISION_BLOCK,
    OP_WRITE, OP_EDIT,
    utc_now_iso, new_id,
)
from agentx_evolve.security.initiator_compat import InitiatorCompat


GUARD_RULE_L0 = "FILE_CHANGE_GUARD_L0"
GUARD_RULE_PROTECTED = "FILE_CHANGE_GUARD_PROTECTED"
GUARD_RULE_BOUNDARY = "FILE_CHANGE_GUARD_BOUNDARY"
GUARD_RULE_GOVERNANCE = "FILE_CHANGE_GUARD_GOVERNANCE"


class FileChangeGuard:
    def __init__(
        self,
        repo_root: Path,
        policy: SandboxPolicy,
        compat: InitiatorCompat | None = None,
    ):
        self._repo_root = repo_root.resolve()
        self._policy = policy
        self._compat = compat

    def check_change_allowed(
        self,
        target_file: str,
        implementation_session_id: str | None = None,
        governance_decision_id: str | None = None,
    ) -> SandboxDecision:
        boundary = check_path_boundary(
            target_file, self._repo_root, OP_EDIT, self._policy,
        )
        if boundary.decision != DECISION_ALLOW:
            return boundary

        try:
            resolved = (self._repo_root / target_file).resolve()
            repo_rel = str(resolved.relative_to(self._repo_root))
        except (ValueError, OSError):
            return SandboxDecision(
                decision_id=new_id("decision"),
                timestamp=utc_now_iso(),
                operation=OP_EDIT,
                target=target_file,
                decision=DECISION_BLOCK,
                reason="Target file is outside repository",
                applied_rule_ids=[GUARD_RULE_BOUNDARY],
            )

        if is_l0_path(repo_rel):
            return SandboxDecision(
                decision_id=new_id("decision"),
                timestamp=utc_now_iso(),
                operation=OP_EDIT,
                target=repo_rel,
                decision=DECISION_BLOCK,
                reason="L0 file change is not allowed",
                applied_rule_ids=[GUARD_RULE_L0],
            )

        if is_protected_path(repo_rel, self._policy):
            return SandboxDecision(
                decision_id=new_id("decision"),
                timestamp=utc_now_iso(),
                operation=OP_EDIT,
                target=repo_rel,
                decision=DECISION_BLOCK,
                reason="Protected path change is not allowed",
                applied_rule_ids=[GUARD_RULE_PROTECTED],
            )

        if not governance_decision_id:
            return SandboxDecision(
                decision_id=new_id("decision"),
                timestamp=utc_now_iso(),
                operation=OP_EDIT,
                target=repo_rel,
                decision=DECISION_BLOCK,
                reason="Governance decision ID required for source change",
                applied_rule_ids=[GUARD_RULE_GOVERNANCE],
            )

        if not implementation_session_id:
            return SandboxDecision(
                decision_id=new_id("decision"),
                timestamp=utc_now_iso(),
                operation=OP_EDIT,
                target=repo_rel,
                decision=DECISION_BLOCK,
                reason="Implementation session ID required for source change",
                applied_rule_ids=[GUARD_RULE_GOVERNANCE],
            )

        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            source_component="FileChangeGuard",
            operation=OP_EDIT,
            target=repo_rel,
            decision=DECISION_ALLOW,
            reason="File change allowed by policy",
            applied_rule_ids=["FILE_CHANGE_GUARD_ALLOW"],
        )

    def verify_changed_files(
        self,
        expected_paths: list[str],
        actual_changed: list[str],
    ) -> list[str]:
        violations: list[str] = []
        expected_set = set(expected_paths)
        actual_set = set(actual_changed)

        unexpected = actual_set - expected_set
        for path in sorted(unexpected):
            violations.append(f"Unexpected change: {path}")

        missing = expected_set - actual_set
        for path in sorted(missing):
            violations.append(f"Expected change not found: {path}")

        return violations
