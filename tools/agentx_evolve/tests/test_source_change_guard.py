from __future__ import annotations

from pathlib import Path

from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    new_id,
    utc_now_iso,
    GUARD_PASS,
    GUARD_BLOCKED,
)
from agentx_evolve.patch_execution.source_change_guard import verify_source_changes


class TestVerifySourceChanges:
    def setup_method(self) -> None:
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )

    def test_pass_when_all_changes_approved(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py"],
            before_hashes={"src/main.py": "aaa"},
            after_hashes={"src/main.py": "bbb"},
        )
        assert result.status == GUARD_PASS

    def test_block_unexpected_path(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py"],
            before_hashes={"src/main.py": "aaa", "src/unapproved.py": "xxx"},
            after_hashes={"src/main.py": "bbb", "src/unapproved.py": "yyy"},
        )
        assert result.status == GUARD_BLOCKED
        assert "src/unapproved.py" in result.unexpected_paths

    def test_block_forbidden_l0_path(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py"],
            before_hashes={"src/main.py": "aaa", ".agentx-init/secret": None},
            after_hashes={"src/main.py": "bbb", ".agentx-init/secret": "hash"},
        )
        assert result.status == GUARD_BLOCKED
        assert ".agentx-init/secret" in result.forbidden_paths

    def test_block_forbidden_git_path(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py"],
            before_hashes={"src/main.py": "aaa", ".git/config": None},
            after_hashes={"src/main.py": "bbb", ".git/config": "hash"},
        )
        assert result.status == GUARD_BLOCKED
        assert ".git/config" in result.forbidden_paths

    def test_warns_on_approved_forbidden_path(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py", ".agentx-init/thing"],
            before_hashes={"src/main.py": "aaa"},
            after_hashes={"src/main.py": "bbb"},
        )
        assert any("Approved path is forbidden" in w for w in result.warnings)

    def test_no_changes_returns_pass(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py"],
            before_hashes={"src/main.py": "aaa"},
            after_hashes={"src/main.py": "aaa"},
        )
        assert result.status == GUARD_PASS

    def test_detects_missing_expected_paths(self) -> None:
        result = verify_source_changes(
            self.session,
            repo_root=Path("/tmp"),
            approved_paths=["src/main.py", "src/utils.py"],
            before_hashes={"src/main.py": "aaa"},
            after_hashes={"src/main.py": "bbb"},
        )
        assert "src/utils.py" in result.missing_expected_paths
