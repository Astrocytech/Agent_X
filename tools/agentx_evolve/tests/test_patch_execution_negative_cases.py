from __future__ import annotations

import json
import shutil
import tempfile
import time
from pathlib import Path

from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    PatchOperation,
    PatchApplication,
    SourceChangeGuardResult,
    ImplementationValidationGateResult,
    RollbackSnapshot,
    RollbackRecord,
    new_id,
    utc_now_iso,
    OP_EXACT_EDIT,
    OP_WRITE_FILE,
    OP_CREATE_FILE,
    OP_DELETE_FILE,
    OP_RENAME_FILE,
    OP_PATCH_TEXT,
    MODE_DRY_RUN,
    PATCH_BLOCKED,
    PATCH_FAILED,
    PATCH_DRY_RUN,
    GUARD_PASS,
    GUARD_BLOCKED,
    VALIDATION_BLOCKED,
)
from agentx_evolve.patch_execution.patch_session import (
    create_implementation_session,
    update_implementation_session,
)
from agentx_evolve.patch_execution.session_lock import (
    acquire_lock,
    release_lock,
    check_lock,
    LOCK_TYPE_SESSION,
    LOCK_TYPE_APPLY,
)
from agentx_evolve.patch_execution.rollback_manager import (
    create_rollback_snapshot,
    rollback_session,
    verify_rollback,
)
from agentx_evolve.patch_execution.patch_applier import apply_patch_operations
from agentx_evolve.patch_execution.source_change_guard import verify_source_changes
from agentx_evolve.patch_execution.implementation_validation_gate import run_validation_gate
from agentx_evolve.patch_execution.patch_evidence import (
    append_implementation_history,
    append_patch_application,
    append_source_change_guard_result,
    append_validation_gate_result,
    append_rollback_record,
    write_latest_artifact,
)
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


class TestSessionNegativeCases:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_empty_target_paths_raises_value_error(self) -> None:
        try:
            create_implementation_session(
                repo_root=self.repo_root,
                target_paths=[],
            )
            assert False, "should have raised ValueError"
        except ValueError:
            pass

    def test_update_with_unknown_status_sets_lifecycle_unknown(self) -> None:
        session = create_implementation_session(
            repo_root=self.repo_root,
            target_paths=["src/main.py"],
        )
        updated = update_implementation_session(
            session=session,
            repo_root=self.repo_root,
            status="NONEXISTENT_STATUS",
        )
        assert updated.lifecycle_state == "UNKNOWN"


class TestLockNegativeCases:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_acquire_lock_invalid_type_raises_value_error(self) -> None:
        try:
            acquire_lock(self.repo_root, "INVALID")
            assert False, "should have raised ValueError"
        except ValueError:
            pass

    def test_check_lock_on_locked_lock_returns_active(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        result = check_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert result["status"] == "ACTIVE"

    def test_release_lock_on_already_released_returns_not_found(self) -> None:
        result = release_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert result["status"] == "NOT_FOUND"

    def test_acquire_lock_stale_threshold_zero_returns_stale(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        result = acquire_lock(
            self.repo_root,
            LOCK_TYPE_SESSION,
            stale_threshold_seconds=0,
        )
        assert result["status"] == "STALE"

    def test_release_lock_invalid_type_raises_value_error(self) -> None:
        try:
            release_lock(self.repo_root, "INVALID")
            assert False, "should have raised ValueError"
        except ValueError:
            pass

    def test_check_lock_invalid_type_raises_value_error(self) -> None:
        try:
            check_lock(self.repo_root, "INVALID")
            assert False, "should have raised ValueError"
        except ValueError:
            pass


class TestRollbackNegativeCases:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )
        self.src_dir = self.repo_root / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_rollback_of_nonexistent_file_still_produces_record(self) -> None:
        snap = create_rollback_snapshot(
            self.session, self.repo_root, ["src/nonexistent.py"]
        )
        record = rollback_session(
            self.session, snap, self.repo_root, trigger="TEST",
        )
        assert record.rollback_id.startswith("RB")
        assert record.status == "ROLLED_BACK"
        assert record.session_id == self.session.session_id
        assert record.snapshot_id == snap.snapshot_id

    def test_verify_rollback_failed_when_file_hash_mismatch(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("original content")
        snap = create_rollback_snapshot(
            self.session, self.repo_root, ["src/main.py"]
        )
        main_py.write_text("modified content")
        result = verify_rollback(snap, self.repo_root)
        assert result["status"] == "FAILED"
        assert result["mismatch_count"] >= 1

    def test_snapshot_nonexistent_file_records_existed_before_false(self) -> None:
        snap = create_rollback_snapshot(
            self.session, self.repo_root, ["src/nonexistent.py"]
        )
        assert snap.status == "CREATED"
        assert len(snap.files) == 1
        assert snap.files[0]["existed_before"] is False
        assert snap.files[0]["before_hash"] is None


class TestPatchApplierNegativeCases:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.src_dir = self.repo_root / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py", "src/utils.py"],
            timestamp=utc_now_iso(),
        )
        self.approved_paths = ["src/main.py", "src/utils.py"]
        self.sandbox_policy = default_sandbox_policy(self.repo_root)

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def _make_op(
        self,
        op_type: str = OP_EXACT_EDIT,
        target_path: str = "src/main.py",
        old_text: str | None = "old",
        new_text: str | None = "new",
        content: str | None = None,
        allow_create: bool = False,
    ) -> PatchOperation:
        return PatchOperation(
            operation_id=new_id("op"),
            operation_type=op_type,
            target_path=target_path,
            old_text=old_text,
            new_text=new_text,
            content=content,
            allow_create=allow_create,
        )

    def test_exact_edit_old_text_not_found_blocks_dry_run(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello world")
        op = self._make_op(OP_EXACT_EDIT, "src/main.py", "nonexistent", "replacement")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED
        assert any("OLD_TEXT_NOT_FOUND" in e for e in result.errors)

    def test_exact_edit_multiple_matches_blocks_dry_run(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("replace this and replace this again")
        op = self._make_op(OP_EXACT_EDIT, "src/main.py", "replace this", "replaced")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED
        assert any("MULTIPLE_MATCHES" in e for e in result.errors)

    def test_create_file_with_allow_create_false_fails(self) -> None:
        approved = self.approved_paths + ["src/new.py"]
        op = self._make_op(
            OP_CREATE_FILE, "src/new.py", content="new file content",
            allow_create=False,
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            approved, self.sandbox_policy,
        )
        assert result.status == PATCH_FAILED
        assert any("allow_create=True" in e for e in result.errors)

    def test_absolute_path_blocked(self) -> None:
        op = self._make_op(OP_EXACT_EDIT, "/etc/passwd")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_path_traversal_blocked(self) -> None:
        op = self._make_op(OP_EXACT_EDIT, "src/../.agentx-init/secrets")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_l0_path_blocked(self) -> None:
        op = self._make_op(OP_EXACT_EDIT, ".agentx-init/something")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_delete_file_blocked_in_v1(self) -> None:
        op = self._make_op(OP_DELETE_FILE, "src/main.py")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_rename_file_blocked_in_v1(self) -> None:
        op = self._make_op(OP_RENAME_FILE, "src/main.py")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_patch_text_blocked_in_v1(self) -> None:
        op = self._make_op(OP_PATCH_TEXT, "src/main.py")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_unapproved_path_blocked(self) -> None:
        op = self._make_op(OP_WRITE_FILE, "src/other.py", content="stuff")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_create_file_target_already_exists_blocked(self) -> None:
        (self.src_dir / "utils.py").write_text("existing")
        op = self._make_op(
            OP_CREATE_FILE, "src/utils.py", content="new",
            allow_create=True,
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED
        assert any("already exists" in e for e in result.errors)

    def test_missing_operation_id_fails(self) -> None:
        op = PatchOperation(
            operation_id="",
            operation_type=OP_EXACT_EDIT,
            target_path="src/main.py",
            old_text="old",
            new_text="new",
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_FAILED

    def test_unknown_operation_type_fails(self) -> None:
        op = self._make_op("UNKNOWN_OP", "src/main.py")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_FAILED

    def test_missing_target_path_fails(self) -> None:
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path="",
            old_text="old",
            new_text="new",
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_FAILED

    def test_exact_edit_missing_old_text_or_new_text_fails(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello")
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path="src/main.py",
            old_text=None,
            new_text=None,
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_FAILED

    def test_write_file_missing_content_fails(self) -> None:
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_WRITE_FILE,
            target_path="src/main.py",
            content=None,
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_FAILED

    def test_exact_edit_target_file_not_exists_fails(self) -> None:
        op = self._make_op(OP_EXACT_EDIT, "src/main.py", "old", "new")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_FAILED
        assert any("does not exist" in e for e in result.errors)


class TestSourceGuardNegativeCases:
    def setup_method(self) -> None:
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )

    def test_source_guard_pass_when_no_changes(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py"],
            before_hashes={"src/main.py": "aaa"},
            after_hashes={"src/main.py": "aaa"},
        )
        assert result.status == GUARD_PASS

    def test_source_guard_block_for_agentx_init_changes(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py"],
            before_hashes={"src/main.py": "aaa", ".agentx-init/secret": None},
            after_hashes={"src/main.py": "bbb", ".agentx-init/secret": "hash"},
        )
        assert result.status == GUARD_BLOCKED
        assert ".agentx-init/secret" in result.forbidden_paths

    def test_source_guard_block_for_git_changes(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py"],
            before_hashes={"src/main.py": "aaa", ".git/config": None},
            after_hashes={"src/main.py": "bbb", ".git/config": "hash"},
        )
        assert result.status == GUARD_BLOCKED
        assert ".git/config" in result.forbidden_paths

    def test_source_guard_block_unexpected_path(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py"],
            before_hashes={"src/main.py": "aaa", "src/unapproved.py": "xxx"},
            after_hashes={"src/main.py": "bbb", "src/unapproved.py": "yyy"},
        )
        assert result.status == GUARD_BLOCKED
        assert "src/unapproved.py" in result.unexpected_paths

    def test_source_guard_missing_expected_path(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py", "src/missing.py"],
            before_hashes={"src/main.py": "aaa"},
            after_hashes={"src/main.py": "bbb"},
        )
        assert "src/missing.py" in result.missing_expected_paths


class TestValidationGateNegativeCases:
    def setup_method(self) -> None:
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )
        self.repo_root = Path("/tmp")

    def test_blocked_with_no_commands(self) -> None:
        result = run_validation_gate(self.session, self.repo_root, [])
        assert result.validation_status == VALIDATION_BLOCKED

    def test_blocked_for_rm_rf_command(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [["rm", "-rf", "/"]],
        )
        assert result.validation_status == VALIDATION_BLOCKED

    def test_blocked_for_empty_command(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [[]],
        )
        assert result.validation_status == VALIDATION_BLOCKED

    def test_blocked_for_illegal_interpreter(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [["bash", "-c", "echo hi"]],
        )
        assert result.validation_status == VALIDATION_BLOCKED

    def test_blocked_compileall_outside_repo(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [["python3", "-m", "compileall", "/etc"]],
        )
        assert result.validation_status == VALIDATION_BLOCKED

    def test_blocked_missing_compileall_path(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [["python3", "-m", "compileall"]],
        )
        assert result.validation_status == VALIDATION_BLOCKED


class TestEvidenceNegativeCases:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_append_implementation_history_writes_correct_file(self) -> None:
        result = append_implementation_history(self.session, self.repo_root)
        assert result["status"] == "written"
        path = self.repo_root / ".agentx-init/implementation/implementation_history.jsonl"
        assert path.exists()
        entry = json.loads(path.read_text(encoding="utf-8").strip())
        assert "schema_version" in entry
        assert "event" in entry
        assert entry["event"] == "implementation_history"

    def test_append_patch_application_writes_correct_file(self) -> None:
        app = PatchApplication(
            application_id=new_id("PA"),
            session_id=self.session.session_id,
            mode="DRY_RUN",
            operations=[],
            target_paths=["src/main.py"],
        )
        result = append_patch_application(app, self.repo_root)
        assert result["status"] == "written"
        path = self.repo_root / ".agentx-init/implementation/patch_applications.jsonl"
        assert path.exists()

    def test_append_source_change_guard_writes_correct_file(self) -> None:
        guard = SourceChangeGuardResult(
            guard_id=new_id("SCG"),
            session_id=self.session.session_id,
            approved_paths=["src/main.py"],
            actual_changed_paths=["src/main.py"],
            unexpected_paths=[],
            missing_expected_paths=[],
            forbidden_paths=[],
        )
        result = append_source_change_guard_result(guard, self.repo_root)
        assert result["status"] == "written"
        path = (
            self.repo_root / ".agentx-init/implementation/source_change_guard_results.jsonl"
        )
        assert path.exists()

    def test_append_validation_gate_writes_correct_file(self) -> None:
        vg = ImplementationValidationGateResult(
            validation_gate_id=new_id("VG"),
            session_id=self.session.session_id,
            commands_requested=[],
            commands_allowed=[],
            commands_blocked=[],
            validation_status="PASS",
        )
        result = append_validation_gate_result(vg, self.repo_root)
        assert result["status"] == "written"
        path = self.repo_root / ".agentx-init/implementation/validation_gate_results.jsonl"
        assert path.exists()

    def test_append_rollback_record_writes_correct_file(self) -> None:
        record = RollbackRecord(
            rollback_id=new_id("RB"),
            session_id=self.session.session_id,
            snapshot_id="snap_1",
            trigger="VALIDATION_FAILED",
            restored_files=[],
            removed_created_files=[],
            verification_status="VERIFIED",
        )
        result = append_rollback_record(record, self.repo_root)
        assert result["status"] == "written"
        path = self.repo_root / ".agentx-init/implementation/rollback_history.jsonl"
        assert path.exists()

    def test_write_latest_artifact_creates_json_file(self) -> None:
        data = {"key": "value"}
        result = write_latest_artifact("test_case", data, self.repo_root)
        assert result["status"] == "written"
        path = self.repo_root / ".agentx-init/implementation/latest_test_case.json"
        assert path.exists()
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["data"] == data
        assert loaded["schema_version"] == "1.0"
        assert loaded["event"] == "latest_test_case"
