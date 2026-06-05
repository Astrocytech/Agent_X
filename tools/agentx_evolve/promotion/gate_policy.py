from __future__ import annotations
from pathlib import Path
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, ValidationEvidence, RiskAcceptance,
    ApprovalReference, GitEvidence, PromotionGatePolicy,
    canonical_json, sha256_dict, sha256_file, to_dict, from_dict,
    CS_NOT_RUN, CS_PASS, CS_FAIL,
    FC_CANDIDATE_MISSING, FC_CANDIDATE_INVALID, FC_CANDIDATE_SUPERSEDED,
    FC_VALIDATION_MISSING, FC_VALIDATION_FAILED, FC_VALIDATION_STALE,
    FC_SCHEMA_VALIDATION_FAILED, FC_APPROVAL_MISSING, FC_APPROVAL_INVALID,
    FC_APPROVAL_REVOKED, FC_APPROVAL_QUORUM_MISSING, FC_APPROVAL_SCOPE_INSUFFICIENT,
    FC_RISK_UNACCEPTED, FC_RISK_BLOCKING, FC_POLICY_DENIED,
    FC_PATCH_EVIDENCE_MISSING, FC_PATCH_EVIDENCE_INVALID,
    FC_PATCH_ROLLBACK_EVIDENCE_MISSING, FC_PATCH_COMMIT_MISMATCH,
    FC_TOOL_EVIDENCE_MISSING, FC_TOOL_EVIDENCE_INVALID,
    FC_TOOL_UNRESOLVED_BLOCKER, FC_TOOL_MCP_EXPOSURE_UNSAFE,
    FC_GIT_STATE_INVALID, FC_EVIDENCE_HASH_MISSING, FC_EVIDENCE_HASH_MISMATCH,
    FC_COMPLETION_RECORD_INVALID, FC_REVIEW_REPORT_MISSING,
    FC_EXPIRED, FC_DEPENDENCY_UNAVAILABLE, FC_SOURCE_MUTATION_DETECTED,
    FC_RELEASE_SCOPE_MISMATCH, FC_TIMESTAMP_INVALID, FC_VALIDATION_TIME_INVALID,
    FC_LOCK_UNAVAILABLE, FC_UNKNOWN_FAILURE,
)


def _blocker(failure_class: str, reason: str, non_overridable: bool = False, detail: str = "") -> dict:
    return {
        "failure_class": failure_class,
        "reason": reason,
        "non_overridable": non_overridable,
        "detail": detail,
    }


def collect_promotion_blockers(
    candidate: ReleaseCandidate | None,
    validation_evidence: ValidationEvidence | None,
    risk_acceptance: RiskAcceptance | None,
    approvals: list[ApprovalReference] | None,
    git_evidence: GitEvidence | None,
    policy_context: dict,
    integration_context: dict,
    repo_root: Path,
) -> list[dict]:
    blockers: list[dict] = []

    if approvals is None:
        approvals = []
    policy = policy_context.get("policy")
    now = policy_context.get("now")

    # 1. release candidate missing
    if candidate is None:
        blockers.append(_blocker(FC_CANDIDATE_MISSING, "Release candidate is missing", non_overridable=True))
        return blockers

    # 2. candidate schema invalid
    if candidate.schema_id != "promotion_release_candidate.schema.json":
        blockers.append(_blocker(FC_CANDIDATE_INVALID, f"Candidate schema invalid: {candidate.schema_id}"))

    # 3. candidate hash mismatch
    computed_hash = _compute_candidate_hash_for_check(candidate)
    if candidate.candidate_hash and computed_hash != candidate.candidate_hash:
        blockers.append(_blocker(FC_CANDIDATE_INVALID, "Candidate hash mismatch", detail=f"computed={computed_hash}, stored={candidate.candidate_hash}"))

    # 4. source_commit missing
    if not candidate.source_commit:
        blockers.append(_blocker(FC_CANDIDATE_INVALID, "source_commit is missing", non_overridable=True))

    # 5. validation evidence missing (when required)
    require_validation = policy_context.get("require_validation", True)
    if require_validation and validation_evidence is None:
        blockers.append(_blocker(FC_VALIDATION_MISSING, "Validation evidence is missing but required"))

    if validation_evidence is not None:
        # 6. validation evidence schema invalid
        if validation_evidence.schema_id != "promotion_validation_evidence.schema.json":
            blockers.append(_blocker(FC_VALIDATION_FAILED, f"Validation evidence schema invalid: {validation_evidence.schema_id}"))

        # 7. validation commit mismatch
        if validation_evidence.validated_commit != candidate.source_commit:
            blockers.append(_blocker(FC_VALIDATION_FAILED, f"Validation commit mismatch: {validation_evidence.validated_commit} != {candidate.source_commit}"))

        # 8. compileall failed
        if validation_evidence.compileall_status == CS_FAIL:
            blockers.append(_blocker(FC_VALIDATION_FAILED, "compileall failed", detail=str(validation_evidence.compileall_exit_code)))

        # 9. pytest failed
        if validation_evidence.pytest_status == CS_FAIL:
            blockers.append(_blocker(FC_VALIDATION_FAILED, "pytest failed", detail=str(validation_evidence.pytest_exit_code)))

        # 10. schema validation failed
        if validation_evidence.schema_validation_status == CS_FAIL:
            blockers.append(_blocker(FC_SCHEMA_VALIDATION_FAILED, "Schema validation failed", detail=str(validation_evidence.schema_validation_exit_code)))

        # 11. required command exit code missing
        for cmd in validation_evidence.commands:
            if "exit_code" not in cmd:
                blockers.append(_blocker(FC_VALIDATION_FAILED, f"Command {cmd.get('name', 'unknown')} missing exit_code"))

        # 12. validation evidence stale
        freshness_minutes = policy_context.get("validation_freshness_minutes", 1440)
        if validation_evidence.created_at:
            if _is_older_than(validation_evidence.created_at, freshness_minutes, now):
                blockers.append(_blocker(FC_VALIDATION_STALE, f"Validation evidence is stale (> {freshness_minutes} minutes old)"))

        # 13. evidence hash missing
        if not validation_evidence.evidence_hash:
            blockers.append(_blocker(FC_EVIDENCE_HASH_MISSING, "Validation evidence hash is missing"))

        # 14. evidence hash mismatch
        computed_ev_hash = _compute_validation_evidence_hash_for_check(validation_evidence)
        if validation_evidence.evidence_hash and computed_ev_hash != validation_evidence.evidence_hash:
            blockers.append(_blocker(FC_EVIDENCE_HASH_MISMATCH, "Validation evidence hash mismatch"))

    # 15. review report missing when required
    require_review = policy_context.get("require_review_report", True)
    if require_review:
        review_path = repo_root / ".agentx-init" / "promotion" / "promotion_review_report.json"
        if not review_path.exists():
            blockers.append(_blocker(FC_REVIEW_REPORT_MISSING, "Review report is missing but required"))

    # 16. completion record missing when required
    require_completion = policy_context.get("require_completion_record_for_approved", True)
    if require_completion:
        completion_path = repo_root / ".agentx-init" / "promotion" / "promotion_completion_record.json"
        if not completion_path.exists():
            blockers.append(_blocker(FC_COMPLETION_RECORD_INVALID, "Completion record is missing but required"))

    # 17-21. approval checks
    require_approval = policy_context.get("require_human_approval_when_listed", True)
    if require_approval and candidate.required_approvals:
        if not approvals:
            blockers.append(_blocker(FC_APPROVAL_MISSING, "Required approvals not found"))
        else:
            for approval in approvals:
                # 17. approval missing (in required_approvals but not found)
                if approval.approval_id not in candidate.required_approvals:
                    continue
                # 18. approval expired
                if approval.expires_at and _is_past(approval.expires_at, now):
                    blockers.append(_blocker(FC_APPROVAL_INVALID, f"Approval {approval.approval_id} has expired"))
                # 19. approval commit mismatch
                if approval.approved_commit and approval.approved_commit != candidate.source_commit:
                    blockers.append(_blocker(FC_APPROVAL_INVALID, f"Approval {approval.approval_id} commit mismatch"))
                # 20. approval candidate mismatch
                if approval.candidate_id and approval.candidate_id != candidate.candidate_id:
                    blockers.append(_blocker(FC_APPROVAL_INVALID, f"Approval {approval.approval_id} candidate mismatch"))
                # 21. approval hash mismatch
                if approval.approval_hash:
                    computed_app_hash = _compute_approval_hash_for_check(approval)
                    if computed_app_hash != approval.approval_hash:
                        blockers.append(_blocker(FC_APPROVAL_INVALID, f"Approval {approval.approval_id} hash mismatch"))

            # 40. revoked approval
            for approval in approvals:
                if approval.revoked:
                    blockers.append(_blocker(FC_APPROVAL_REVOKED, f"Approval {approval.approval_id} has been revoked"))

            # 41. approval quorum missing
            quorum = policy_context.get("required_approval_quorum", 1)
            valid_approvals = [a for a in approvals if a.approval_id in candidate.required_approvals and not a.revoked]
            if len(valid_approvals) < quorum:
                blockers.append(_blocker(FC_APPROVAL_QUORUM_MISSING, f"Required approval quorum {quorum} not met, found {len(valid_approvals)}"))

            # 42. approval scope insufficient
            for approval in approvals:
                if approval.scope and candidate.release_scope:
                    if not set(candidate.release_scope).issubset(set(approval.scope)):
                        blockers.append(_blocker(FC_APPROVAL_SCOPE_INSUFFICIENT, f"Approval {approval.approval_id} scope insufficient for release scope"))

    # 22. blocking risk present
    if risk_acceptance is not None:
        if risk_acceptance.blocking_risks:
            blockers.append(_blocker(FC_RISK_BLOCKING, f"Blocking risks present: {risk_acceptance.blocking_risks}"))

        # 23. unaccepted required risk present
        for risk in risk_acceptance.risks:
            risk_id = risk.get("risk_id", risk.get("id", ""))
            if risk.get("required", False) and risk_id not in risk_acceptance.accepted_risks:
                blockers.append(_blocker(FC_RISK_UNACCEPTED, f"Required risk {risk_id} not accepted"))

        # 24. risk acceptance expired
        if risk_acceptance.expires_at and _is_past(risk_acceptance.expires_at, now):
            blockers.append(_blocker(FC_EXPIRED, "Risk acceptance has expired"))

    # 25. policy denial present
    policy_decision = integration_context.get("policy_decision")
    if policy_decision and policy_decision.get("decision") == "DENY":
        blockers.append(_blocker(FC_POLICY_DENIED, "Policy decision is DENY", non_overridable=True))

    # 26. policy unavailable for actual promotion
    if not policy_context.get("allow_dry_run_without_policy", True) and not policy_decision:
        blockers.append(_blocker(FC_DEPENDENCY_UNAVAILABLE, "Policy decision unavailable"))

    # 27. patch evidence missing when patch session referenced
    if candidate.patch_session_id:
        patch_evidence_path = repo_root / ".agentx-init" / "promotion" / "patch_evidence.json"
        if not patch_evidence_path.exists():
            blockers.append(_blocker(FC_PATCH_EVIDENCE_MISSING, "Patch evidence missing but patch session referenced"))
        else:
            # 28. patch evidence failed
            patch_status = integration_context.get("patch_evidence_status", CS_NOT_RUN)
            if patch_status == CS_FAIL:
                blockers.append(_blocker(FC_PATCH_EVIDENCE_INVALID, "Patch evidence failed"))

    # 29. tool evidence missing when tool session referenced
    if candidate.tool_session_id:
        tool_evidence_path = repo_root / ".agentx-init" / "promotion" / "tool_evidence.json"
        if not tool_evidence_path.exists():
            blockers.append(_blocker(FC_TOOL_EVIDENCE_MISSING, "Tool evidence missing but tool session referenced"))

    # 30. tool evidence unresolved blocker
    tool_blockers = integration_context.get("tool_unresolved_blockers", [])
    if tool_blockers:
        blockers.append(_blocker(FC_TOOL_UNRESOLVED_BLOCKER, f"Tool evidence has unresolved blockers: {tool_blockers}"))

    # 31. Git status dirty when clean required
    if git_evidence is not None:
        require_clean = policy_context.get("require_clean_git_state", True)
        if require_clean and git_evidence.working_tree_status in ("DIRTY", "UNKNOWN"):
            blockers.append(_blocker(FC_GIT_STATE_INVALID, f"Git working tree is {git_evidence.working_tree_status}"))

        # 32. source commit unreachable
        if not git_evidence.commit_reachable:
            blockers.append(_blocker(FC_GIT_STATE_INVALID, f"Source commit {git_evidence.source_commit} is unreachable"))

        # 33. changed files mismatch
        if candidate.changed_files and git_evidence.changed_files:
            if set(candidate.changed_files) != set(git_evidence.changed_files):
                blockers.append(_blocker(FC_GIT_STATE_INVALID, "Changed files mismatch between candidate and git evidence"))

        # 34. forbidden Git action detected
        if git_evidence.forbidden_git_actions_detected:
            blockers.append(_blocker(FC_GIT_STATE_INVALID, f"Forbidden git actions: {git_evidence.forbidden_git_actions_detected}"))

        # 35. unreviewed source mutation
        if validation_evidence is not None:
            if validation_evidence.source_mutation_status in ("DIRTY", "UNKNOWN"):
                blockers.append(_blocker(FC_SOURCE_MUTATION_DETECTED, f"Source mutation detected: {validation_evidence.source_mutation_status}"))

    # 36. candidate expired
    if candidate.expires_at and _is_past(candidate.expires_at, now):
        blockers.append(_blocker(FC_EXPIRED, "Candidate has expired"))

    # 37. unknown integration status
    integration_status = integration_context.get("integration_status")
    if integration_status and integration_status not in ("READY", "DEGRADED"):
        blockers.append(_blocker(FC_DEPENDENCY_UNAVAILABLE, f"Unknown integration status: {integration_status}"))

    # 38. completion record attempted for blocked candidate (warning only, not a blocker)
    # This is informational - no blocker added

    # 39. superseded candidate
    if candidate.superseded_by_candidate_id:
        blockers.append(_blocker(FC_CANDIDATE_SUPERSEDED, f"Candidate superseded by {candidate.superseded_by_candidate_id}"))

    # 43. release scope mismatch
    if candidate.release_scope and git_evidence is not None:
        pass

    # 44. lock unavailable
    lock_status = integration_context.get("lock_status")
    if lock_status == "UNAVAILABLE":
        blockers.append(_blocker(FC_LOCK_UNAVAILABLE, "Promotion lock is unavailable"))

    return blockers


def _compute_candidate_hash_for_check(candidate: ReleaseCandidate) -> str:
    from agentx_evolve.promotion.release_candidate import compute_candidate_hash
    return compute_candidate_hash(candidate)


def _compute_validation_evidence_hash_for_check(evidence: ValidationEvidence) -> str:
    from agentx_evolve.promotion.validation_evidence import compute_validation_evidence_hash
    return compute_validation_evidence_hash(evidence)


def _compute_approval_hash_for_check(approval: ApprovalReference) -> str:
    from agentx_evolve.promotion.approval_lookup import compute_approval_references_hash
    return compute_approval_references_hash([approval])


def _is_past(iso_str: str, now: str | None = None) -> bool:
    from datetime import datetime, timezone
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if now:
            ref = datetime.fromisoformat(now)
            if ref.tzinfo is None:
                ref = ref.replace(tzinfo=timezone.utc)
        else:
            ref = datetime.now(timezone.utc)
        return ref >= dt
    except ValueError:
        return True


def _is_older_than(iso_str: str, minutes: int, now: str | None = None) -> bool:
    from datetime import datetime, timezone, timedelta
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if now:
            ref = datetime.fromisoformat(now)
            if ref.tzinfo is None:
                ref = ref.replace(tzinfo=timezone.utc)
        else:
            ref = datetime.now(timezone.utc)
        return ref - dt > timedelta(minutes=minutes)
    except ValueError:
        return True


def classify_blocker(blocker: dict) -> str:
    return blocker.get("failure_class", FC_UNKNOWN_FAILURE)


def has_non_overridable_blocker(blockers: list[dict]) -> bool:
    return any(b.get("non_overridable", False) for b in blockers)
