from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    DECISION_ALLOW,
    DECISION_BLOCK,
    DECISION_DRY_RUN_ONLY,
    RESTORE_STATUS_BLOCKED,
    RESTORE_STATUS_PLANNED,
    RESTORE_MODE_DRY_RUN,
    BackupManifest,
    RestoreDecision,
    RestorePlan,
    RestoreRequest,
    new_id,
    resolve_repo_root,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)
from agentx_evolve.backup.restore_preflight import build_restore_preflight_record


def _restore_plan_path(repo_root: Path, plan_id: str) -> Path:
    from agentx_evolve.backup.backup_models import restore_plans_dir
    return restore_plans_dir(repo_root) / (plan_id + ".plan.json")


def _orig_create_restore_decision(
    request: RestoreRequest,
    preflight: "RestorePreflightRecord",
    policy_decisions: dict | None = None,
) -> RestoreDecision:
    if policy_decisions is None:
        policy_decisions = {}

    blockers = preflight.blockers
    if blockers:
        decision = DECISION_BLOCK
        reason = "Preflight checks failed: " + "; ".join(blockers)
    elif request.dry_run:
        decision = DECISION_DRY_RUN_ONLY
        reason = "DRY_RUN mode; no destructive actions taken"
    elif request.restore_mode in ("SOURCE_RESTORE", "FULL_RECOVERY"):
        decision = DECISION_BLOCK
        reason = "Source/full restore blocked by default in v1"
    elif request.restore_mode == "RUNTIME_ONLY":
        decision = DECISION_ALLOW
        reason = "Runtime-only restore permitted"
    else:
        decision = DECISION_BLOCK
        reason = "Unknown restore mode: " + request.restore_mode

    return RestoreDecision(
        restore_decision_id=new_id("rd"),
        restore_request_id=request.restore_request_id,
        decided_at=utc_now_iso(),
        decision=decision,
        reason=reason,
        destructive_actions_allowed=not request.dry_run and decision == DECISION_ALLOW,
    )


def _orig_plan_restore(
    request: RestoreRequest,
    manifest: BackupManifest,
    decision: RestoreDecision,
    repo_root: Path | None = None,
) -> RestorePlan:
    if repo_root is None:
        repo_root = resolve_repo_root()

    plan_id = new_id("plan")
    files_to_restore: list[str] = []
    conflicts: list[str] = []
    destructive_actions: list[str] = []
    blocked_reasons: list[str] = []

    if decision.decision == DECISION_BLOCK:
        blocked_reasons.append(decision.reason)
    else:
        for record in manifest.file_records:
            if not record.included:
                continue
            target = str(Path(request.target_root) / record.relative_path) if request.target_root else record.original_path
            files_to_restore.append(target)
            if Path(target).exists():
                conflicts.append(target + " (existing)")
                destructive_actions.append("OVERWRITE: " + target)

    plan = RestorePlan(
        restore_plan_id=plan_id,
        restore_request_id=request.restore_request_id,
        backup_id=request.backup_id,
        created_at=utc_now_iso(),
        restore_mode=request.restore_mode,
        dry_run=request.dry_run,
        restore_decision_id=decision.restore_decision_id,
        files_to_restore=files_to_restore,
        conflicts=conflicts,
        destructive_actions=destructive_actions,
        blocked_reasons=blocked_reasons,
        status=RESTORE_STATUS_BLOCKED if blocked_reasons else RESTORE_STATUS_PLANNED,
    )

    path = _restore_plan_path(repo_root, plan_id)
    write_json_atomic(path, to_dict(plan))
    return plan


def create_restore_decision(
    restore_request: RestoreRequest,
    manifest: BackupManifest,
    verification: "BackupVerificationResult",
    policy: BackupPolicy,
    context: dict,
) -> RestoreDecision:
    """SPEC 10.8-compliant wrapper."""
    from agentx_evolve.backup.backup_models import BackupVerificationResult
    from agentx_evolve.backup.restore_preflight import _orig_build_restore_preflight_record as build_restore_preflight_record
    preflight = build_restore_preflight_record(
        resolve_repo_root(), restore_request, manifest, verification, policy, context,
    )
    return _orig_create_restore_decision(restore_request, preflight)


def plan_restore(
    repo_root: Path,
    restore_request: RestoreRequest,
    manifest: BackupManifest,
    verification: "BackupVerificationResult",
    policy: BackupPolicy,
    context: dict,
) -> RestorePlan:
    """SPEC 10.8-compliant wrapper."""
    from agentx_evolve.backup.backup_models import BackupVerificationResult
    from agentx_evolve.backup.restore_preflight import _orig_build_restore_preflight_record as build_restore_preflight_record
    preflight = build_restore_preflight_record(repo_root, restore_request, manifest, verification, policy, context)
    decision = _orig_create_restore_decision(restore_request, preflight)
    return _orig_plan_restore(restore_request, manifest, decision, repo_root=repo_root)
