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
    MODE_DRY_RUN,
    MODE_LIVE,
    PATCH_DRY_RUN,
    PATCH_BLOCKED,
)
from agentx_evolve.patch_execution.patch_applier import apply_patch_operations
from agentx_evolve.security.safe_file_ops import safe_read_file, safe_write_file, safe_exact_edit
from agentx_evolve.security.sandbox_policy import default_sandbox_policy, merge_sandbox_policy
from agentx_evolve.security.initiator_compat import InitiatorCompat
from agentx_evolve.patch.patch_models import MutationAllowlist, ApprovedMutation


class TestGovernedPatchExecutionSandboxIntegration:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.src_dir = self.repo_root / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)
        (self.repo_root / "L0").mkdir()
        (self.repo_root / ".agentx-init").mkdir()
        self.policy = default_sandbox_policy(self.repo_root)
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    # -- helpers -----------------------------------------------------------

    def _enable_source_writes(self) -> None:
        self.policy.source_write_allowed = True
        self.policy.require_governance_for_source_write = False
        self.policy.require_session_for_source_write = False
        self.policy.require_rollback_for_source_write = False

    def _make_allowlist(self, *path_prefixes: str) -> MutationAllowlist:
        return MutationAllowlist(
            allowlist_id=new_id("mal"),
            mutations=[
                ApprovedMutation(target_path=p, mutation_id=new_id("m"))
                for p in path_prefixes
            ],
        )

    # -- 1. safe_read_file within repo root -------------------------------

    def test_safe_read_within_repo_root(self) -> None:
        target = self.src_dir / "hello.txt"
        target.write_text("file content")
        result = safe_read_file("src/hello.txt", self.repo_root, self.policy)
        assert result.status == "SUCCESS", result.errors
        assert result.content == "file content"

    # -- 2. safe_write_file blocked without source_write_allowed ----------

    def test_safe_write_blocked_without_source_write_allowed(self) -> None:
        result = safe_write_file("src/new.txt", "data", self.repo_root, self.policy)
        assert result.status == "BLOCKED"

    # -- 3. safe_write_file allowed with source_write_allowed=True --------

    def test_safe_write_allowed_with_source_write_allowed(self) -> None:
        self._enable_source_writes()
        compat = InitiatorCompat(self.repo_root)
        allowlist = self._make_allowlist("src/")
        result = safe_write_file(
            "src/new.txt", "new data", self.repo_root, self.policy,
            implementation_session_id="sess-1",
            governance_decision_id="gov-1",
            rollback_snapshot_id="rb-1",
            compat=compat,
            mutation_allowlist=allowlist,
        )
        assert result.status == "SUCCESS", result.errors
        assert (self.src_dir / "new.txt").read_text() == "new data"

    # -- 4. safe_exact_edit reads, edits, writes --------------------------

    def test_safe_exact_edit_read_edit_write(self) -> None:
        target = self.src_dir / "edit_me.txt"
        target.write_text("before text")
        self._enable_source_writes()
        compat = InitiatorCompat(self.repo_root)
        allowlist = self._make_allowlist("src/")
        result = safe_exact_edit(
            "src/edit_me.txt", "before", "after", self.repo_root, self.policy,
            implementation_session_id="sess-1",
            governance_decision_id="gov-1",
            rollback_snapshot_id="rb-1",
            compat=compat,
            mutation_allowlist=allowlist,
        )
        assert result.status == "SUCCESS", result.errors
        assert target.read_text() == "after text"

    # -- 5. apply_patch_operations DRY_RUN + approved EXACT_EDIT ---------

    def test_dry_run_approved_exact_edit_returns_dry_run(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello old world")
        approved_paths = ["src/main.py"]
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path="src/main.py",
            old_text="old",
            new_text="new",
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            approved_paths, self.policy,
        )
        assert result.status == PATCH_DRY_RUN
        assert "src/main.py" in result.changed_paths
        assert main_py.read_text() == "hello old world"

    # -- 6. apply_patch_operations DRY_RUN blocks unapproved paths --------

    def test_dry_run_blocks_unapproved_path(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("content")
        approved_paths = ["src/approved.py"]
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path="src/main.py",
            old_text="old",
            new_text="new",
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            approved_paths, self.policy,
        )
        assert result.status == PATCH_BLOCKED

    # -- 7. apply_patch_operations DRY_RUN blocks absolute path -----------

    def test_dry_run_blocks_absolute_path(self) -> None:
        approved_paths = ["src/main.py"]
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path="/etc/passwd",
            old_text="root",
            new_text="",
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            approved_paths, self.policy,
        )
        assert result.status == PATCH_BLOCKED

    # -- 8. apply_patch_operations DRY_RUN blocks L0 path -----------------

    def test_dry_run_blocks_l0_path(self) -> None:
        approved_paths = [".agentx-init/mem"]
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path=".agentx-init/mem",
            old_text="old",
            new_text="new",
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_DRY_RUN,
            approved_paths, self.policy,
        )
        assert result.status == PATCH_BLOCKED

    # -- 9. apply_patch_operations LIVE requires rollback_snapshot_id -----

    def test_live_mode_requires_rollback_snapshot_id(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("content")
        approved_paths = ["src/main.py"]
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path="src/main.py",
            old_text="old",
            new_text="new",
        )
        result = apply_patch_operations(
            self.session, [op], self.repo_root, MODE_LIVE,
            approved_paths, self.policy,
        )
        assert result.status == PATCH_BLOCKED
        assert any("rollback_snapshot_id" in e for e in result.errors)

    # -- 10. Default sandbox policy protected_paths -----------------------

    def test_default_policy_protected_paths(self) -> None:
        assert "L0/" in self.policy.protected_paths
        assert "agent_x/runtime/" in self.policy.protected_paths
        assert "core/" in self.policy.protected_paths
        assert ".agentx-init/" in self.policy.allowlisted_write_paths

    # -- 11. merge_sandbox_policy overrides source_write_allowed ----------

    def test_merge_sandbox_policy_overrides_source_write_allowed(self) -> None:
        merged = merge_sandbox_policy(self.policy, {"source_write_allowed": True})
        assert merged.source_write_allowed is True
        assert merged.policy_id == self.policy.policy_id

    # -- 12. Path boundary blocks outside-repo paths ----------------------

    def test_path_boundary_blocks_outside_repo(self) -> None:
        outside = Path(tempfile.mkdtemp()) / "secret.txt"
        outside.write_text("secret data")
        result = safe_read_file(str(outside), self.repo_root, self.policy)
        assert result.status == "BLOCKED"
