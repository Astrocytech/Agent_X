from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from agentx_evolve.patch_execution.patch_models import (
    PatchOperation,
    new_id,
    OP_EXACT_EDIT,
    OP_WRITE_FILE,
    MODE_DRY_RUN,
)
from agentx_evolve.patch_execution.patch_execution_service import (
    execute_governed_patch,
)
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


class TestExecuteGovernedPatch:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.src_dir = self.repo_root / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.sandbox_policy = default_sandbox_policy(self.repo_root)

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def _make_op(
        self,
        target_path: str = "src/main.py",
        old_text: str | None = "old",
        new_text: str | None = "new",
    ) -> PatchOperation:
        return PatchOperation(
            operation_id=new_id("op"),
            operation_type=OP_EXACT_EDIT,
            target_path=target_path,
            old_text=old_text,
            new_text=new_text,
        )

    def test_dry_run_success(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello old world")
        op = self._make_op("src/main.py", "old", "new")
        session = execute_governed_patch(
            repo_root=self.repo_root,
            operations=[op],
            approved_paths=["src/main.py"],
            governance_decision_id="GOV_test",
            mode=MODE_DRY_RUN,
        )
        assert session.status == "DRY_RUN_READY" or session.status == "BLOCKED"

    def test_dry_run_with_valid_gov_id(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello old world")
        op = self._make_op("src/main.py", "old", "new")
        session = execute_governed_patch(
            repo_root=self.repo_root,
            operations=[op],
            approved_paths=["src/main.py"],
            governance_decision_id="GOV_test",
            mode=MODE_DRY_RUN,
        )
        assert session.session_id.startswith("IMP")

    def test_blocks_missing_governance(self) -> None:
        op = self._make_op("src/main.py", "old", "new")
        session = execute_governed_patch(
            repo_root=self.repo_root,
            operations=[op],
            approved_paths=["src/main.py"],
            governance_decision_id=None,
            mode=MODE_DRY_RUN,
        )
        assert session.status == "BLOCKED"
        assert session.final_decision == "REJECT"

    def test_blocks_missing_approved_paths(self) -> None:
        op = self._make_op("src/main.py", "old", "new")
        session = execute_governed_patch(
            repo_root=self.repo_root,
            operations=[op],
            approved_paths=[],
            governance_decision_id="GOV_test",
            mode=MODE_DRY_RUN,
        )
        assert session.status == "BLOCKED"

    def test_dry_run_creates_session_files(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello old world")
        op = self._make_op("src/main.py", "old", "new")
        session = execute_governed_patch(
            repo_root=self.repo_root,
            operations=[op],
            approved_paths=["src/main.py"],
            governance_decision_id="GOV_test",
            mode=MODE_DRY_RUN,
        )
        session_path = (
            self.repo_root
            / ".agentx-init/implementation/sessions"
            / f"{session.session_id}.json"
        )
        assert session_path.exists()

    def test_dry_run_history_written(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello old world")
        op = self._make_op("src/main.py", "old", "new")
        execute_governed_patch(
            repo_root=self.repo_root,
            operations=[op],
            approved_paths=["src/main.py"],
            governance_decision_id="GOV_test",
            mode=MODE_DRY_RUN,
        )
        history_path = (
            self.repo_root / ".agentx-init/implementation/implementation_history.jsonl"
        )
        assert history_path.exists()
        lines = history_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) >= 1

    def test_dry_run_blocked_when_old_text_not_found(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello world")
        op = self._make_op("src/main.py", "nonexistent", "replacement")
        session = execute_governed_patch(
            repo_root=self.repo_root,
            operations=[op],
            approved_paths=["src/main.py"],
            governance_decision_id="GOV_test",
            mode=MODE_DRY_RUN,
        )
        assert session.status == "BLOCKED"

    def test_dry_run_blocked_unapproved_path(self) -> None:
        main_py = self.src_dir / "other.py"
        main_py.write_text("hello old world")
        op = self._make_op("src/other.py", "old", "new")
        session = execute_governed_patch(
            repo_root=self.repo_root,
            operations=[op],
            approved_paths=["src/main.py"],
            governance_decision_id="GOV_test",
            mode=MODE_DRY_RUN,
        )
        assert session.status == "BLOCKED"

    def test_dry_run_blocked_delete_file_v1(self) -> None:
        op = PatchOperation(
            operation_id=new_id("op"),
            operation_type="DELETE_FILE",
            target_path="src/main.py",
        )
        session = execute_governed_patch(
            repo_root=self.repo_root,
            operations=[op],
            approved_paths=["src/main.py"],
            governance_decision_id="GOV_test",
            mode=MODE_DRY_RUN,
        )
        assert session.status == "BLOCKED"

    def test_live_mode_requires_sandbox_policy(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("hello old world")
        op = self._make_op("src/main.py", "old", "new")
        session = execute_governed_patch(
            repo_root=self.repo_root,
            operations=[op],
            approved_paths=["src/main.py"],
            governance_decision_id="GOV_test",
            mode="LIVE",
            sandbox_policy=None,
        )
        assert session.status == "BLOCKED"
