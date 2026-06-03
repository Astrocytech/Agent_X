from __future__ import annotations
from pathlib import Path
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, ValidationEvidence, RiskAcceptance,
    ApprovalReference, GitEvidence, PromotionGateDecision,
    PC_APPROVED, PC_BLOCKED, PC_FAILED, PC_INVALID,
    PD_PROMOTE, PD_BLOCK,
    FC_CANDIDATE_MISSING, FC_CANDIDATE_INVALID,
    FC_EVIDENCE_HASH_MISSING, FC_EVIDENCE_HASH_MISMATCH,
    FC_VALIDATION_MISSING, FC_EXPIRED, FC_LOCK_UNAVAILABLE,
    write_json_atomic, append_jsonl, to_dict, sha256_dict, sha256_file,
    canonical_json,
)
from agentx_evolve.promotion.release_candidate import (
    load_release_candidate, validate_release_candidate,
)
from agentx_evolve.promotion.validation_evidence import (
    load_validation_evidence, verify_evidence_hashes,
)
from agentx_evolve.promotion.risk_acceptance import (
    load_risk_acceptance,
)
from agentx_evolve.promotion.approval_lookup import (
    load_approval_references,
)
from agentx_evolve.promotion.git_evidence import (
    load_git_evidence,
)
from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
from agentx_evolve.promotion.gate_decision import create_gate_decision
from agentx_evolve.promotion.gate_recorder import (
    acquire_promotion_lock, release_promotion_lock,
    append_gate_decision_history, write_latest_gate_decision,
    append_blocked_promotion, append_invalid_promotion,
    LockUnavailableError,
)
from agentx_evolve.promotion.promotion_expiry import (
    validate_candidate_freshness, validate_evidence_freshness,
    validate_approval_freshness, validate_risk_acceptance_freshness,
)
from agentx_evolve.promotion.promotion_report import (
    create_promotion_evidence_manifest, write_promotion_review_report,
    write_promotion_completion_record,
)
from agentx_evolve.promotion.dependency_adapters import (
    check_policy_dependency, check_human_approval_dependency,
    check_patch_evidence_dependency, check_tool_evidence_dependency,
    check_git_dependency, classify_failure_dependency,
)


def run_promotion_gate(
    candidate_path: Path,
    repo_root: Path,
    policy_context: dict | None = None,
    dry_run: bool = False,
) -> PromotionGateDecision:
    if policy_context is None:
        policy_context = {}
    integration_context: dict = {
        "policy_decision": None,
        "patch_evidence_status": "NOT_RUN",
        "tool_unresolved_blockers": [],
        "integration_status": "READY",
        "lock_status": None,
    }

    try:
        # Step 2: Load ReleaseCandidate
        candidate = load_release_candidate(candidate_path)
        if candidate is None:
            return _build_failed_decision(
                "Release candidate could not be loaded from {candidate_path}",
                dry_run,
            )

        # Step 3: Validate ReleaseCandidate schema and candidate_hash
        val_errors = validate_release_candidate(candidate)
        if val_errors:
            integration_context["candidate_status"] = "INVALID"
            decision = create_gate_decision(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context=policy_context,
                integration_context=integration_context,
                repo_root=repo_root,
                dry_run=dry_run,
            )
            decision.blocking_failures = [
                {"failure_class": FC_CANDIDATE_INVALID, "reason": e} for e in val_errors
            ]
            decision.errors.extend(val_errors)
            _record_decision(decision, repo_root)
            return decision

        # Step 4: Load ValidationEvidence if present or required
        validation_evidence = _load_validation_evidence(repo_root)
        if validation_evidence:
            integration_context["validation_status"] = "LOADED"
        else:
            integration_context["validation_status"] = "NOT_FOUND"

        # Step 5: Load RiskAcceptance if present or required
        risk_acceptance = _load_risk_acceptance(repo_root)

        # Step 6: Load ApprovalReference list
        approvals = _load_approval_references(repo_root)

        # Step 7: Load GitEvidence if present or required
        git_evidence = _load_git_evidence(repo_root)

        # Step 8: Verify expiry for candidate, validation evidence, approvals, risk acceptance
        expiry_errors: list[str] = []
        expiry_errors.extend(validate_candidate_freshness(candidate))
        if validation_evidence:
            freshness = policy_context.get("validation_freshness_minutes", 1440)
            expiry_errors.extend(validate_evidence_freshness(validation_evidence, freshness))
        if approvals:
            expiry_errors.extend(validate_approval_freshness(approvals))
        if risk_acceptance:
            expiry_errors.extend(validate_risk_acceptance_freshness(risk_acceptance))
        if expiry_errors:
            integration_context["expiry_status"] = "EXPIRED"
        else:
            integration_context["expiry_status"] = "FRESH"

        # Step 9: Verify evidence hashes
        hash_errors: list[str] = []
        if validation_evidence:
            hash_errors.extend(verify_evidence_hashes(validation_evidence, repo_root))
        if hash_errors:
            integration_context["hash_status"] = "MISMATCH"
        else:
            integration_context["hash_status"] = "VERIFIED"

        # Step 10: Check Policy / Capability Registry
        policy_result = check_policy_dependency(
            candidate, "promotion_gate", policy_context, dry_run,
        )
        if policy_result["status"] in ("BLOCKED", "FAILED"):
            integration_context["policy_decision"] = {
                "decision": "DENY",
                "reason": policy_result["reason"],
                "policy_decision_id": "",
            }
            integration_context["policy_status"] = policy_result["status"]
        elif policy_result["status"] == "NOT_AVAILABLE":
            integration_context["policy_status"] = "NOT_AVAILABLE"
        else:
            integration_context["policy_status"] = "PASS"
        integration_lock_context = policy_context.copy()
        integration_lock_context["lock_timeout_seconds"] = policy_context.get(
            "lock_timeout_seconds", 10,
        )
        stale_lock = policy_context.get("stale_lock_age_seconds", 900)
        allow_stale = policy_context.get("allow_stale_lock_recovery", False)
        integration_lock_context["stale_lock_age_seconds"] = stale_lock
        integration_lock_context["allow_stale_lock_recovery"] = allow_stale

        # Step 11: Check Human Approval references
        approval_result = check_human_approval_dependency(candidate, approvals)
        if approval_result["status"] == "FAILED":
            integration_context["approval_status"] = "FAILED"
        elif approval_result["status"] == "NOT_AVAILABLE":
            integration_context["approval_status"] = "DEGRADED"
        else:
            integration_context["approval_status"] = "PASS"

        # Step 12: Check Governed Patch Execution evidence
        patch_result = check_patch_evidence_dependency(candidate, repo_root)
        if patch_result["status"] == "FAILED":
            integration_context["patch_evidence_status"] = "FAIL"
            integration_context["integration_status"] = "DEGRADED"
        elif patch_result["status"] == "PASS":
            integration_context["patch_evidence_status"] = "PASS"
        elif patch_result["status"] == "NOT_AVAILABLE":
            integration_context["patch_evidence_status"] = "NOT_AVAILABLE"
            integration_context["integration_status"] = "DEGRADED"

        # Step 13: Check Tool / MCP Adapter evidence
        tool_result = check_tool_evidence_dependency(candidate, repo_root)
        if tool_result["status"] == "FAILED":
            integration_context["tool_unresolved_blockers"] = [tool_result["reason"]]
            integration_context["integration_status"] = "DEGRADED"
        elif tool_result["status"] == "NOT_AVAILABLE":
            integration_context["integration_status"] = "DEGRADED"

        # Step 14: Check Git evidence and source commit reachability
        git_result = check_git_dependency(candidate, git_evidence, repo_root)
        if git_result["status"] in ("FAILED", "BLOCKED"):
            integration_context["git_status"] = "FAILED"
        elif git_result["status"] == "NOT_AVAILABLE":
            integration_context["git_status"] = "DEGRADED"
        else:
            integration_context["git_status"] = "PASS"

        # Step 15: Collect all blockers
        blockers = collect_promotion_blockers(
            candidate, validation_evidence, risk_acceptance,
            approvals, git_evidence, policy_context,
            integration_context, repo_root,
        )

        # Step 16: Create PromotionGateDecision
        decision = create_gate_decision(
            candidate, validation_evidence, risk_acceptance,
            approvals, git_evidence, policy_context,
            integration_context, repo_root, dry_run,
        )
        decision.blocking_failures = blockers

        # Step 17: Acquire promotion lock
        try:
            acquire_promotion_lock(
                repo_root,
                timeout_seconds=policy_context.get("lock_timeout_seconds", 10),
                stale_lock_age_seconds=policy_context.get("stale_lock_age_seconds", 900),
                allow_stale_lock_recovery=policy_context.get("allow_stale_lock_recovery", False),
            )
            integration_context["lock_status"] = "ACQUIRED"
        except LockUnavailableError as exc:
            integration_context["lock_status"] = "UNAVAILABLE"
            decision.errors.append(str(exc))
            if not decision.blocking_failures:
                decision.blocking_failures = []
            decision.blocking_failures.append({
                "failure_class": FC_LOCK_UNAVAILABLE,
                "reason": str(exc),
            })
            decision.status = PC_BLOCKED
            decision.decision = PD_BLOCK
            decision.reason = "Promotion lock unavailable"

        # Step 18: Record decision history
        _record_decision_history(decision, repo_root)

        # Step 19: Write latest gate decision
        write_latest_gate_decision(decision, repo_root)

        # Step 20: Write evidence manifest and review report
        evidence_files = _collect_evidence_files(repo_root)
        manifest = create_promotion_evidence_manifest(
            candidate, decision, evidence_files, repo_root,
        )
        if manifest:
            decision.evidence_manifest_path = manifest.get("manifest_id", "")
            decision.evidence_manifest_sha256 = manifest.get("manifest_hash", "")
        report_path = write_promotion_review_report(candidate, decision, repo_root)
        if report_path:
            decision.review_report_path = str(report_path.relative_to(repo_root))
            decision.review_report_sha256 = sha256_file(report_path)

        # Step 21: Write completion record only if APPROVED/PROMOTE and not dry_run
        completion_path = None
        if decision.status == PC_APPROVED and decision.decision == PD_PROMOTE and not dry_run:
            completion_path = write_promotion_completion_record(candidate, decision, repo_root)
            if completion_path:
                decision.completion_record_path = str(completion_path.relative_to(repo_root))
                decision.completion_record_sha256 = sha256_file(completion_path)

        # Step 22: Release lock
        release_promotion_lock(repo_root)

        # Step 23: Return PromotionGateDecision
        return decision

    except Exception as exc:
        try:
            release_promotion_lock(repo_root)
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to release promotion lock during error unwinding")
        return _build_failed_decision(
            str(exc),
            dry_run,
            errors=[str(exc)],
        )


def _build_failed_decision(
    reason: str,
    dry_run: bool,
    errors: list[str] | None = None,
) -> PromotionGateDecision:
    from agentx_evolve.models.model_models import new_id, utc_now_iso
    decision = PromotionGateDecision(
        decision_id=new_id("gd-"),
        created_at=utc_now_iso(),
        decision=PD_BLOCK,
        status=PC_FAILED,
        reason=reason,
        dry_run=dry_run,
        errors=errors or [reason],
    )
    decision.blocking_failures = [
        {"failure_class": FC_CANDIDATE_MISSING, "reason": reason},
    ]
    return decision


def _load_validation_evidence(repo_root: Path) -> ValidationEvidence | None:
    path = repo_root / ".agentx-init" / "promotion" / "validation_evidence.json"
    if not path.exists():
        return None
    try:
        return load_validation_evidence(path)
    except Exception:
        return None


def _load_risk_acceptance(repo_root: Path) -> RiskAcceptance | None:
    path = repo_root / ".agentx-init" / "promotion" / "risk_acceptance.json"
    if not path.exists():
        return None
    try:
        return load_risk_acceptance(path)
    except Exception:
        return None


def _load_approval_references(repo_root: Path) -> list[ApprovalReference]:
    path = repo_root / ".agentx-init" / "promotion" / "approval_references.jsonl"
    try:
        return load_approval_references(path)
    except Exception:
        return []


def _load_git_evidence(repo_root: Path) -> GitEvidence | None:
    path = repo_root / ".agentx-init" / "promotion" / "git_evidence.json"
    if not path.exists():
        return None
    try:
        return load_git_evidence(path)
    except Exception:
        return None


def _record_decision(decision: PromotionGateDecision, repo_root: Path) -> None:
    try:
        write_latest_gate_decision(decision, repo_root)
        append_gate_decision_history(decision, repo_root)
        if decision.status in ("BLOCKED", "FAILED"):
            append_blocked_promotion(decision, repo_root)
        elif decision.status == "INVALID":
            append_invalid_promotion(decision, repo_root)
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed to record promotion decision")


def _record_decision_history(decision: PromotionGateDecision, repo_root: Path) -> None:
    try:
        append_gate_decision_history(decision, repo_root)
        if decision.status in ("BLOCKED", "FAILED"):
            append_blocked_promotion(decision, repo_root)
        elif decision.status == "INVALID":
            append_invalid_promotion(decision, repo_root)
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed to record promotion decision history")


def _collect_evidence_files(repo_root: Path) -> list[Path]:
    evidence_dir = repo_root / ".agentx-init" / "promotion"
    if not evidence_dir.is_dir():
        return []
    files: list[Path] = []
    try:
        for f in sorted(evidence_dir.iterdir()):
            if f.is_file() and f.suffix in (".json", ".jsonl"):
                files.append(f)
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed to collect evidence files")
    return files
