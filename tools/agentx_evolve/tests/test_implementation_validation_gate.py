from __future__ import annotations

from pathlib import Path

from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    new_id,
    utc_now_iso,
    VALIDATION_PASS,
    VALIDATION_BLOCKED,
)
from agentx_evolve.patch_execution.implementation_validation_gate import (
    run_validation_gate,
)


class TestRunValidationGate:
    def setup_method(self) -> None:
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )
        self.repo_root = Path("/tmp/test_repo")

    def test_blocked_when_no_commands(self) -> None:
        result = run_validation_gate(self.session, self.repo_root, [])
        assert result.validation_status == VALIDATION_BLOCKED

    def test_compileall_allowed(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [["python3", "-m", "compileall", str(self.repo_root / "tools/agentx_evolve")]],
        )
        assert result.validation_status == VALIDATION_PASS

    def test_pytest_allowed_in_tests_dir(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [["python3", "-m", "pytest", str(self.repo_root / "tools/agentx_evolve/tests/test_example.py")]],
        )
        assert result.validation_status == VALIDATION_PASS

    def test_blocked_unknown_command(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [["rm", "-rf", "/"]],
        )
        assert result.validation_status == VALIDATION_BLOCKED

    def test_blocked_compileall_outside_repo(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [["python3", "-m", "compileall", "/etc"]],
        )
        assert result.validation_status == VALIDATION_BLOCKED

    def test_blocked_pytest_outside_tests_dir(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [["python3", "-m", "pytest", str(self.repo_root / "src")]],
        )
        assert result.validation_status == VALIDATION_BLOCKED

    def test_blocked_empty_command(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [[]],
        )
        assert result.validation_status == VALIDATION_BLOCKED

    def test_blocked_illegal_interpreter(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [["bash", "-c", "echo hi"]],
        )
        assert result.validation_status == VALIDATION_BLOCKED

    def test_records_requested_allowed_blocked(self) -> None:
        result = run_validation_gate(
            self.session,
            self.repo_root,
            [
                ["python3", "-m", "compileall", str(self.repo_root / "tools/agentx_evolve")],
                ["rm", "-rf", "/"],
            ],
        )
        assert len(result.commands_requested) == 2
        assert len(result.commands_allowed) == 1
        assert len(result.commands_blocked) == 1
