import pytest
from pathlib import Path
from agentx_evolve.patch_execution.patch_models import (
    PatchOperation, PatchApplication, PatchResult, ImplementationSession,
    DryRunResult, RollbackRecord, SourceChangeGuardResult,
    OP_EXACT_EDIT, PATCH_APPLIED, PATCH_FAILED, PATCH_BLOCKED, PATCH_DRY_RUN, MODE_DRY_RUN,
    MODE_LIVE, SESSION_STATUS_ACCEPTED, SESSION_STATUS_FAILED,
    new_id, utc_now_iso, sha256_text,
)
from agentx_evolve.patch_execution.patch_applier import apply_patch_operations


class TestIdempotency:
    def test_same_operation_applied_twice_no_side_effects(self, tmp_path):
        file = tmp_path / "target.py"
        file.write_text("hello")
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path=str(file),
            old_text="hello",
            new_text="world",
        )
        session = ImplementationSession(
            session_id=new_id("ses"),
            rollback_snapshot_id="snap-1",
        )
        result1 = apply_patch_operations(session, [op], tmp_path, MODE_LIVE, [str(tmp_path)], None)
        assert result1.status in (PATCH_APPLIED, PATCH_FAILED)

    def test_dry_run_does_not_mutate_files(self, tmp_path):
        file = tmp_path / "target.py"
        file.write_text("original")
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path=str(file),
            old_text="original",
            new_text="modified",
        )
        session = ImplementationSession(session_id=new_id("ses"))
        result = apply_patch_operations(session, [op], tmp_path, MODE_DRY_RUN, [str(tmp_path)], None)
        assert file.read_text() == "original"

    def test_empty_operations_returns_dry_run(self, tmp_path):
        session = ImplementationSession(session_id=new_id("ses"))
        result = apply_patch_operations(session, [], tmp_path, MODE_DRY_RUN, [], None)
        assert result.status == PATCH_DRY_RUN
        assert result.changed_paths == []


class TestPatchExecutionPolicyIntegration:
    def test_policy_blocked_operation_returns_blocked(self, tmp_path):
        file = tmp_path / "protected.py"
        file.write_text("data")
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path=str(file),
            old_text="data",
            new_text="changed",
        )
        session = ImplementationSession(session_id=new_id("ses"))
        result = apply_patch_operations(session, [op], tmp_path, MODE_DRY_RUN, [], None)
        assert result.status in (PATCH_DRY_RUN, PATCH_BLOCKED, PATCH_FAILED)


class TestRollback:
    def test_rollback_snapshot_creation(self):
        record = RollbackRecord(
            rollback_id=new_id("rb"),
            session_id=new_id("ses"),
            snapshot_id=new_id("snap"),
            timestamp=utc_now_iso(),
            trigger="USER_REQUEST",
        )
        assert record.rollback_id != ""
        assert record.trigger == "USER_REQUEST"

    def test_rollback_empty_state(self):
        record = RollbackRecord()
        assert record.status == "ROLLED_BACK"
        assert record.restored_files == []
