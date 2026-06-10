import json, os, sys, tempfile
from pathlib import Path
from agentx_evolve.patch_execution.patch_applier import apply_patch_operations
from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession, PatchOperation, MODE_DRY_RUN, MODE_LIVE,
    OP_EXACT_EDIT, OP_CREATE_FILE, SESSION_STATUS_CREATED,
)
from agentx_evolve.patch_execution.rollback_manager import (
    create_rollback_snapshot, rollback_session,
)


class TestPatchExecutionFlow:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.repo_root = self.tmpdir / "repo"
        self.repo_root.mkdir()
        self.session = ImplementationSession(
            session_id="test-session-001",
            status=SESSION_STATUS_CREATED,
            rollback_snapshot_id="snap-001",
            lifecycle_state="CREATED",
        )
        self.approved_paths = ["src/"]

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_valid_patch_applies_in_temp_workspace(self):
        target = self.repo_root / "src"
        target.mkdir(parents=True)
        src_file = target / "hello.txt"
        src_file.write_text("hello world")
        ops = [
            PatchOperation(
                operation_id="op-1", operation_type=OP_EXACT_EDIT,
                target_path="src/hello.txt",
                old_text="hello world", new_text="hello agentx",
            )
        ]
        self.session.rollback_snapshot_id = None
        result = apply_patch_operations(
            self.session, ops, self.repo_root, MODE_DRY_RUN,
            self.approved_paths, None,
        )
        assert result.status == "DRY_RUN"
        assert "src/hello.txt" in result.changed_paths

    def test_invalid_path_patch_is_rejected(self):
        ops = [
            PatchOperation(
                operation_id="op-2", operation_type=OP_EXACT_EDIT,
                target_path="../../../etc/passwd",
                old_text="root", new_text="hacked",
            )
        ]
        result = apply_patch_operations(
            self.session, ops, self.repo_root, MODE_DRY_RUN,
            self.approved_paths, None,
        )
        assert result.status in ("BLOCKED", "FAILED")
        assert any("traversal" in e.lower() for e in result.errors)

    def test_dry_run_reports_planned_changes_without_modifying(self):
        target = self.repo_root / "src"
        target.mkdir(parents=True)
        src_file = target / "dry_test.txt"
        src_file.write_text("original content")
        ops = [
            PatchOperation(
                operation_id="op-3", operation_type=OP_EXACT_EDIT,
                target_path="src/dry_test.txt",
                old_text="original content", new_text="modified content",
            )
        ]
        self.session.rollback_snapshot_id = None
        result = apply_patch_operations(
            self.session, ops, self.repo_root, MODE_DRY_RUN,
            self.approved_paths, None,
        )
        assert result.status == "DRY_RUN"
        assert src_file.read_text() == "original content"

    def test_rollback_restores_source_state(self):
        target = self.repo_root / "src"
        target.mkdir(parents=True)
        src_file = target / "rollback_test.txt"
        src_file.write_text("before state")
        paths = ["src/rollback_test.txt"]
        snapshot = create_rollback_snapshot(self.session, self.repo_root, paths)
        src_file.write_text("after state")
        record = rollback_session(
            self.session, snapshot, self.repo_root, "USER_REQUEST",
        )
        assert record.status == "ROLLED_BACK"
        assert src_file.read_text() == "before state"
