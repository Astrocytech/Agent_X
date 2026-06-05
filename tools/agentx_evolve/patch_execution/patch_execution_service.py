from __future__ import annotations

from pathlib import Path

from agentx_evolve.patch_execution.patch_evidence import (
    build_patch_execution_audit_event,
    write_latest_artifact,
)
from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    PatchOperation,
    new_id,
    to_dict,
    utc_now_iso,
    MODE_DRY_RUN,
    MODE_LIVE,
    SOURCE_COMPONENT,
)
from agentx_evolve.patch_execution.patch_session import (
    create_implementation_session,
    update_implementation_session,
)
from agentx_evolve.patch_execution.session_lock import acquire_lock, release_lock
from agentx_evolve.patch_execution.rollback_manager import (
    create_rollback_snapshot,
    rollback_session,
)
from agentx_evolve.patch_execution.patch_applier import apply_patch_operations
from agentx_evolve.patch_execution.source_change_guard import verify_source_changes
from agentx_evolve.patch_execution.implementation_validation_gate import (
    run_validation_gate,
)

from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat


def execute_governed_patch(
    repo_root: Path,
    operations: list[PatchOperation],
    approved_paths: list[str],
    proposal_id: str | None = None,
    governance_decision_id: str | None = None,
    policy_decision_id: str | None = None,
    mode: str = MODE_DRY_RUN,
    validation_commands: list[list[str]] | None = None,
    sandbox_policy: object | None = None,
    compat: InitiatorPatchCompat | None = None,
) -> ImplementationSession:
    target_paths = list({op.target_path for op in operations if op.target_path})

    if not governance_decision_id:
        session = create_implementation_session(
            repo_root, target_paths, proposal_id, None, policy_decision_id, compat
        )
        session = update_implementation_session(
            session, repo_root, "BLOCKED",
            final_decision="REJECT",
            errors=["governance_decision_id is required"],
            compat=compat,
        )
        return session

    if not approved_paths:
        session = create_implementation_session(
            repo_root, target_paths, proposal_id, governance_decision_id, policy_decision_id, compat
        )
        session = update_implementation_session(
            session, repo_root, "BLOCKED",
            final_decision="REJECT",
            errors=["approved_paths must not be empty"],
            compat=compat,
        )
        return session

    lock_result = acquire_lock(
        repo_root, "IMPLEMENTATION_SESSION",
        session_id=None, stale_threshold_seconds=300, force=False, compat=compat,
    )
    if lock_result["status"] not in ("ACQUIRED", "STALE"):
        session = create_implementation_session(
            repo_root, target_paths, proposal_id, governance_decision_id, policy_decision_id, compat
        )
        session = update_implementation_session(
            session, repo_root, "BLOCKED",
            final_decision="REJECT",
            errors=[f"could not acquire session lock: {lock_result.get('reason', 'unknown')}"],
            compat=compat,
        )
        return session

    session = create_implementation_session(
        repo_root, target_paths, proposal_id, governance_decision_id, policy_decision_id, compat
    )

    try:
        if mode == MODE_DRY_RUN:
            session = update_implementation_session(
                session, repo_root, "DRY_RUNNING", compat=compat,
            )
            patch_result = apply_patch_operations(
                session, operations, repo_root, MODE_DRY_RUN,
                approved_paths, sandbox_policy, compat,
            )
            if patch_result.status in ("BLOCKED", "FAILED"):
                session = update_implementation_session(
                    session, repo_root, "BLOCKED",
                    final_decision="REJECT",
                    errors=patch_result.errors,
                    warnings=patch_result.warnings,
                    compat=compat,
                )
                return session
            write_latest_artifact("patch_result", to_dict(patch_result), repo_root, compat)
            session = update_implementation_session(
                session, repo_root, "DRY_RUN_READY",
                final_decision="PENDING",
                changed_paths=patch_result.changed_paths,
                compat=compat,
            )
            return session

        if mode == MODE_LIVE:
            session = update_implementation_session(
                session, repo_root, "LIVE_APPROVED", compat=compat,
            )
            if sandbox_policy is None:
                session = update_implementation_session(
                    session, repo_root, "BLOCKED",
                    final_decision="REJECT",
                    errors=["LIVE mode requires sandbox_policy"],
                    compat=compat,
                )
                return session

            session = update_implementation_session(
                session, repo_root, "PATCH_RUNNING", compat=compat,
            )
            rollback_snapshot = create_rollback_snapshot(
                session, repo_root, target_paths, compat,
            )
            session.rollback_snapshot_id = rollback_snapshot.snapshot_id

            patch_result = apply_patch_operations(
                session, operations, repo_root, MODE_LIVE,
                approved_paths, sandbox_policy, compat,
            )

            if patch_result.status in ("BLOCKED", "FAILED"):
                rollback_record = rollback_session(
                    session, rollback_snapshot, repo_root,
                    trigger="PATCH_FAILED",
                    created_paths=patch_result.created_paths,
                    compat=compat,
                )
                session.rollback_record_id = rollback_record.rollback_id
                write_latest_artifact("rollback_record", to_dict(rollback_record), repo_root, compat)
                write_latest_artifact("patch_result", to_dict(patch_result), repo_root, compat)
                session = update_implementation_session(
                    session, repo_root, "ROLLED_BACK",
                    final_decision="ROLLBACK",
                    changed_paths=patch_result.changed_paths,
                    rollback_snapshot_id=rollback_snapshot.snapshot_id,
                    patch_application_id=patch_result.application_id,
                    errors=patch_result.errors,
                    warnings=patch_result.warnings,
                    compat=compat,
                )
                return session

            write_latest_artifact("patch_result", to_dict(patch_result), repo_root, compat)
            session = update_implementation_session(
                session, repo_root, "PATCH_APPLIED",
                changed_paths=patch_result.changed_paths,
                patch_application_id=patch_result.application_id,
                rollback_snapshot_id=rollback_snapshot.snapshot_id,
                compat=compat,
            )

            session = update_implementation_session(
                session, repo_root, "VALIDATION_RUNNING", compat=compat,
            )
            guard_result = verify_source_changes(
                session, repo_root, approved_paths,
                patch_result.before_hashes, patch_result.after_hashes, compat,
            )
            session.source_change_guard_id = guard_result.guard_id

            if guard_result.status != "PASS":
                rollback_record = rollback_session(
                    session, rollback_snapshot, repo_root,
                    trigger="SOURCE_GUARD_FAILED",
                    created_paths=patch_result.created_paths,
                    compat=compat,
                )
                session.rollback_record_id = rollback_record.rollback_id
                write_latest_artifact("rollback_record", to_dict(rollback_record), repo_root, compat)
                session = update_implementation_session(
                    session, repo_root, "ROLLED_BACK",
                    final_decision="ROLLBACK",
                    source_change_guard_id=guard_result.guard_id,
                    errors=guard_result.warnings + guard_result.errors,
                    compat=compat,
                )
                return session

            validation_gate_result = run_validation_gate(
                session, repo_root, validation_commands or [], compat,
            )
            session.validation_result_id = validation_gate_result.validation_gate_id

            if validation_gate_result.validation_status != "PASS":
                rollback_record = rollback_session(
                    session, rollback_snapshot, repo_root,
                    trigger="VALIDATION_FAILED",
                    created_paths=patch_result.created_paths,
                    compat=compat,
                )
                session.rollback_record_id = rollback_record.rollback_id
                write_latest_artifact("rollback_record", to_dict(rollback_record), repo_root, compat)
                session = update_implementation_session(
                    session, repo_root, "ROLLED_BACK",
                    final_decision="ROLLBACK",
                    source_change_guard_id=guard_result.guard_id,
                    validation_result_id=validation_gate_result.validation_gate_id,
                    errors=[validation_gate_result.reason],
                    compat=compat,
                )
                return session

            session = update_implementation_session(
                session, repo_root, "ACCEPTED",
                final_decision="ACCEPT",
                source_change_guard_id=guard_result.guard_id,
                validation_result_id=validation_gate_result.validation_gate_id,
                compat=compat,
            )
            return session

        session = update_implementation_session(
            session, repo_root, "FAILED",
            final_decision="REJECT",
            errors=[f"unknown mode: {mode}"],
            compat=compat,
        )
        return session

    except Exception as e:
        session = update_implementation_session(
            session, repo_root, "FAILED",
            final_decision="REJECT",
            errors=[f"unexpected error: {e}"],
            compat=compat,
        )
        return session
    finally:
        release_lock(repo_root, "IMPLEMENTATION_SESSION", session_id=session.session_id, compat=compat)
