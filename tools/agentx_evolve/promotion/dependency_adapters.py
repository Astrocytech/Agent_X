from __future__ import annotations
from pathlib import Path
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, FC_DEPENDENCY_UNAVAILABLE, FC_UNKNOWN_FAILURE,
)


def _dep_result(
    status: str,
    failure_class: str | None = None,
    reason: str = "",
    evidence_refs: list | None = None,
    warnings: list | None = None,
    errors: list | None = None,
) -> dict:
    return {
        "status": status,
        "failure_class": failure_class,
        "reason": reason,
        "evidence_refs": evidence_refs or [],
        "warnings": warnings or [],
        "errors": errors or [],
    }


def check_policy_dependency(
    candidate: ReleaseCandidate,
    caller_role: str,
    policy_context: dict,
    dry_run: bool,
) -> dict:
    try:
        from agentx_evolve.policy.policy_decision import check_policy_allowed
        policy_decision = check_policy_allowed(
            component_id=candidate.component_id,
            caller_role=caller_role,
            action="promote",
            context=policy_context,
            dry_run=dry_run,
        )
        if policy_decision and policy_decision.get("decision") == "DENY":
            return _dep_result(
                status="BLOCKED",
                failure_class=FC_DEPENDENCY_UNAVAILABLE,
                reason=policy_decision.get("reason", "Policy denied promotion"),
                evidence_refs=[policy_decision.get("policy_decision_id", "")],
            )
        return _dep_result(
            status="PASS",
            reason="Policy check passed",
            evidence_refs=[policy_decision.get("policy_decision_id", "")] if policy_decision else [],
        )
    except ImportError:
        return _dep_result(
            status="NOT_AVAILABLE",
            failure_class=FC_DEPENDENCY_UNAVAILABLE,
            reason="Policy/Capability Registry module not available",
        )
    except Exception as exc:
        return _dep_result(
            status="NOT_AVAILABLE",
            failure_class=FC_DEPENDENCY_UNAVAILABLE,
            reason=f"Policy dependency check failed: {exc}",
            errors=[str(exc)],
        )


def check_human_approval_dependency(
    candidate: ReleaseCandidate,
    approvals: list,
) -> dict:
    try:
        from agentx_evolve.human_review.approval_lookup import (
            find_active_approval_for_action, validate_approval_id,
        )
        if not approvals:
            return _dep_result(
                status="NOT_APPLICABLE",
                reason="No approvals provided to check",
            )
        errors: list[str] = []
        warnings: list[str] = []
        for approval in approvals:
            if hasattr(approval, "approval_id"):
                aid = approval.approval_id
            elif isinstance(approval, dict):
                aid = approval.get("approval_id", "")
            else:
                aid = ""
            if not aid:
                continue
            try:
                val_result = validate_approval_id(aid, candidate.candidate_id, Path("."))
                if not val_result:
                    warnings.append(f"Approval {aid} could not be validated")
            except Exception:
                warnings.append(f"Approval {aid} validation skipped (dependency degraded)")
        return _dep_result(
            status="PASS" if not errors else "FAILED",
            reason="Human approval dependency checked" if not errors else "; ".join(errors),
            warnings=warnings,
            errors=errors,
        )
    except ImportError:
        return _dep_result(
            status="NOT_AVAILABLE",
            failure_class=FC_DEPENDENCY_UNAVAILABLE,
            reason="Human approval module not available",
        )
    except Exception as exc:
        return _dep_result(
            status="NOT_AVAILABLE",
            failure_class=FC_DEPENDENCY_UNAVAILABLE,
            reason=f"Human approval dependency check failed: {exc}",
            errors=[str(exc)],
        )


def check_patch_evidence_dependency(
    candidate: ReleaseCandidate,
    repo_root: Path,
) -> dict:
    if not candidate.patch_session_id:
        return _dep_result(
            status="NOT_APPLICABLE",
            reason="No patch_session_id on candidate",
        )
    try:
        from agentx_evolve.patch_session.patch_evidence import (
            load_patch_evidence, validate_patch_evidence,
        )
        evidence_path = repo_root / ".agentx-init" / "patch_evidence" / f"{candidate.patch_session_id}.json"
        if not evidence_path.exists():
            return _dep_result(
                status="FAILED",
                failure_class="PROMOTION_PATCH_EVIDENCE_MISSING",
                reason=f"Patch evidence not found at {evidence_path}",
                errors=[f"File not found: {evidence_path}"],
            )
        evidence = load_patch_evidence(evidence_path)
        val_errors = validate_patch_evidence(evidence, candidate.patch_session_id)
        if val_errors:
            return _dep_result(
                status="FAILED",
                failure_class="PROMOTION_PATCH_EVIDENCE_INVALID",
                reason="Patch evidence validation failed",
                errors=val_errors,
                evidence_refs=[str(evidence_path)],
            )
        return _dep_result(
            status="PASS",
            reason="Patch evidence validated",
            evidence_refs=[str(evidence_path)],
        )
    except ImportError:
        return _dep_result(
            status="NOT_AVAILABLE",
            failure_class=FC_DEPENDENCY_UNAVAILABLE,
            reason="Patch evidence module not available (graceful degradation)",
        )
    except Exception as exc:
        return _dep_result(
            status="NOT_AVAILABLE",
            failure_class=FC_DEPENDENCY_UNAVAILABLE,
            reason=f"Patch evidence dependency check failed: {exc}",
            errors=[str(exc)],
        )


def check_tool_evidence_dependency(
    candidate: ReleaseCandidate,
    repo_root: Path,
) -> dict:
    if not candidate.tool_session_id:
        return _dep_result(
            status="NOT_APPLICABLE",
            reason="No tool_session_id on candidate",
        )
    try:
        from agentx_evolve.tool_registry.tool_evidence import (
            load_tool_evidence, validate_tool_evidence,
        )
        evidence_path = repo_root / ".agentx-init" / "tool_evidence" / f"{candidate.tool_session_id}.json"
        if not evidence_path.exists():
            return _dep_result(
                status="FAILED",
                failure_class="PROMOTION_TOOL_EVIDENCE_MISSING",
                reason=f"Tool evidence not found at {evidence_path}",
                errors=[f"File not found: {evidence_path}"],
            )
        evidence = load_tool_evidence(evidence_path)
        val_errors = validate_tool_evidence(evidence, candidate.tool_session_id)
        if val_errors:
            return _dep_result(
                status="FAILED",
                failure_class="PROMOTION_TOOL_EVIDENCE_INVALID",
                reason="Tool evidence validation failed",
                errors=val_errors,
                evidence_refs=[str(evidence_path)],
            )
        return _dep_result(
            status="PASS",
            reason="Tool evidence validated",
            evidence_refs=[str(evidence_path)],
        )
    except ImportError:
        return _dep_result(
            status="NOT_AVAILABLE",
            failure_class=FC_DEPENDENCY_UNAVAILABLE,
            reason="Tool evidence module not available (graceful degradation)",
        )
    except Exception as exc:
        return _dep_result(
            status="NOT_AVAILABLE",
            failure_class=FC_DEPENDENCY_UNAVAILABLE,
            reason=f"Tool evidence dependency check failed: {exc}",
            errors=[str(exc)],
        )


def check_git_dependency(
    candidate: ReleaseCandidate,
    git_evidence: object,
    repo_root: Path,
) -> dict:
    try:
        from agentx_evolve.git.git_operations import check_commit_reachable
        source_commit = candidate.source_commit
        if not source_commit:
            return _dep_result(
                status="FAILED",
                failure_class="PROMOTION_GIT_STATE_INVALID",
                reason="No source_commit on candidate to verify",
                errors=["source_commit is empty"],
            )
        reachable = check_commit_reachable(source_commit, repo_root)
        if not reachable:
            return _dep_result(
                status="FAILED",
                failure_class="PROMOTION_GIT_STATE_INVALID",
                reason=f"Source commit {source_commit} is not reachable",
                errors=[f"Commit {source_commit} not found in repository history"],
            )
        return _dep_result(
            status="PASS",
            reason=f"Source commit {source_commit} is reachable",
        )
    except ImportError:
        return _dep_result(
            status="NOT_AVAILABLE",
            failure_class=FC_DEPENDENCY_UNAVAILABLE,
            reason="Git operations module not available (graceful degradation)",
        )
    except Exception as exc:
        return _dep_result(
            status="NOT_AVAILABLE",
            failure_class=FC_DEPENDENCY_UNAVAILABLE,
            reason=f"Git dependency check failed: {exc}",
            errors=[str(exc)],
        )


def classify_failure_dependency(blocker: dict) -> dict:
    failure_class = blocker.get("failure_class", FC_UNKNOWN_FAILURE)
    reason = blocker.get("reason", "")
    severity_map: dict[str, str] = {
        "PROMOTION_CANDIDATE_MISSING": "CRITICAL",
        "PROMOTION_CANDIDATE_INVALID": "CRITICAL",
        "PROMOTION_POLICY_DENIED": "CRITICAL",
        "PROMOTION_DEPENDENCY_UNAVAILABLE": "HIGH",
        "PROMOTION_GIT_STATE_INVALID": "HIGH",
        "PROMOTION_EVIDENCE_HASH_MISMATCH": "HIGH",
        "PROMOTION_APPROVAL_MISSING": "HIGH",
        "PROMOTION_APPROVAL_INVALID": "HIGH",
        "PROMOTION_APPROVAL_REVOKED": "HIGH",
        "PROMOTION_VALIDATION_FAILED": "MEDIUM",
        "PROMOTION_VALIDATION_STALE": "MEDIUM",
        "PROMOTION_EXPIRED": "MEDIUM",
        "PROMOTION_TOOL_EVIDENCE_MISSING": "MEDIUM",
        "PROMOTION_PATCH_EVIDENCE_MISSING": "MEDIUM",
        "PROMOTION_LOCK_UNAVAILABLE": "LOW",
    }
    severity = severity_map.get(failure_class, "UNKNOWN")
    non_overridable = blocker.get("non_overridable", False)
    return {
        "failure_class": failure_class,
        "severity": severity,
        "reason": reason,
        "non_overridable": non_overridable,
        "classification": "HARD_BLOCK" if non_overridable else "SOFT_BLOCK",
    }
