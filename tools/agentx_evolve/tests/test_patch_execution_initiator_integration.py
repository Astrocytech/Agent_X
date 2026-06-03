from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat


class TestInitiatorPatchCompat:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_init_with_repo_root(self) -> None:
        compat = InitiatorPatchCompat(self.repo_root)
        assert compat.get_repo_root() == self.repo_root

    def test_init_without_repo_root(self) -> None:
        compat = InitiatorPatchCompat()
        assert compat.get_repo_root() == Path(".")

    def test_get_runtime_state_root(self) -> None:
        compat = InitiatorPatchCompat(self.repo_root)
        assert compat.get_runtime_state_root() == self.repo_root / ".agentx-init"

    def test_load_proposal_returns_error_on_not_found(self) -> None:
        compat = InitiatorPatchCompat(self.repo_root)
        result = compat.load_proposal("prop_1")
        assert "error" in result
        assert "not found" in result["error"]

    def test_load_governance_decision_returns_error_on_not_found(self) -> None:
        compat = InitiatorPatchCompat(self.repo_root)
        result = compat.load_governance_decision("gov_1")
        assert "error" in result
        assert "not found" in result["error"]

    def test_validate_schema_skips_when_schema_not_found(self) -> None:
        compat = InitiatorPatchCompat(self.repo_root)
        result = compat.validate_schema({"test": True}, "test.schema.json")
        assert "valid" in result
        assert "warning" in result

    def test_write_json_atomic_creates_file(self) -> None:
        compat = InitiatorPatchCompat(self.repo_root)
        path = self.repo_root / "test.json"
        result = compat.write_json_atomic(path, {"key": "value"})
        assert result["success"] is True
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["key"] == "value"

    def test_write_json_atomic_creates_parent_dirs(self) -> None:
        compat = InitiatorPatchCompat(self.repo_root)
        path = self.repo_root / "sub/dir/test.json"
        result = compat.write_json_atomic(path, {"k": "v"})
        assert result["success"] is True

    def test_append_jsonl_appends_line(self) -> None:
        compat = InitiatorPatchCompat(self.repo_root)
        path = self.repo_root / "test.jsonl"
        compat.append_jsonl(path, {"event": "first"})
        compat.append_jsonl(path, {"event": "second"})
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2

    def test_append_audit_event(self) -> None:
        compat = InitiatorPatchCompat(self.repo_root)
        result = compat.append_audit_event({"event": "test"})
        assert result["success"] is True
        audit_path = self.repo_root / ".agentx-init/memory/audit_events.jsonl"
        assert audit_path.exists()

    def test_run_validation_command_succeeds(self) -> None:
        compat = InitiatorPatchCompat(self.repo_root)
        result = compat.run_validation_command(["python3", "--version"])
        assert result["success"] is True
        assert result["returncode"] == 0
        assert "Python" in result["stdout"]
