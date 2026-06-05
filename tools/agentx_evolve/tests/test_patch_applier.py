from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    PatchOperation,
    new_id,
    utc_now_iso,
    OP_EXACT_EDIT,
    OP_WRITE_FILE,
    OP_CREATE_FILE,
    OP_DELETE_FILE,
    OP_RENAME_FILE,
    OP_PATCH_TEXT,
    MODE_DRY_RUN,
    MODE_LIVE,
    PATCH_DRY_RUN,
    PATCH_APPLIED,
    PATCH_BLOCKED,
    PATCH_FAILED,
)
from agentx_evolve.patch_execution.patch_applier import apply_patch_operations
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


class TestApplyPatchOperations:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.src_dir = self.repo_root / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
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

    def test_dry_run_exact_edit(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello old world")
        op = self._make_op(OP_EXACT_EDIT, "src/main.py", "old", "new")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_DRY_RUN
        assert "src/main.py" in result.changed_paths
        assert main_py.read_text() == "hello old world"

    def test_dry_run_write_file(self) -> None:
        op = self._make_op(OP_WRITE_FILE, "src/main.py", content="new content")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_DRY_RUN
        assert "src/main.py" in result.changed_paths

    def test_dry_run_create_file(self) -> None:
        op = self._make_op(OP_CREATE_FILE, "src/utils.py", content="util", allow_create=True)
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_DRY_RUN
        assert "src/utils.py" in result.changed_paths

    def test_dry_run_create_file_already_exists(self) -> None:
        (self.src_dir / "utils.py").write_text("existing")
        op = self._make_op(OP_CREATE_FILE, "src/utils.py", content="new", allow_create=True)
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_block_delete_file_v1(self) -> None:
        op = self._make_op(OP_DELETE_FILE, "src/main.py")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_block_rename_file_v1(self) -> None:
        op = self._make_op(OP_RENAME_FILE, "src/main.py")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_block_patch_text_v1(self) -> None:
        op = self._make_op(OP_PATCH_TEXT, "src/main.py")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_block_absolute_path(self) -> None:
        op = self._make_op(OP_EXACT_EDIT, "/etc/passwd")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_block_path_traversal(self) -> None:
        op = self._make_op(OP_EXACT_EDIT, "src/../.agentx-init/secrets")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_block_l0_path(self) -> None:
        op = self._make_op(OP_EXACT_EDIT, ".agentx-init/something")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_block_unapproved_path(self) -> None:
        op = self._make_op(OP_EXACT_EDIT, "src/other.py")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED

    def test_block_unknown_operation_type(self) -> None:
        op = self._make_op("UNKNOWN_OP", "src/main.py")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_FAILED

    def test_live_mode_requires_rollback_snapshot(self) -> None:
        op = self._make_op(OP_EXACT_EDIT, "src/main.py")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_LIVE,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED
        assert any("rollback_snapshot_id" in e for e in result.errors)

    def test_dry_run_exact_edit_old_text_not_found(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello world")
        op = self._make_op(OP_EXACT_EDIT, "src/main.py", "nonexistent", "replacement")
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            self.approved_paths, self.sandbox_policy,
        )
        assert result.status == PATCH_BLOCKED
