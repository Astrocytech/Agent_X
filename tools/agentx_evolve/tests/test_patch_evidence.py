from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from agentx_evolve.patch_execution.patch_evidence import (
    append_implementation_history,
    append_patch_application,
    append_source_change_guard_result,
    append_validation_gate_result,
    append_rollback_record,
    write_latest_artifact,
    build_patch_execution_audit_event,
)
from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    PatchApplication,
    SourceChangeGuardResult,
    ImplementationValidationGateResult,
    RollbackRecord,
    new_id,
    utc_now_iso,
)


class TestEvidenceAppend:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def _assert_evidence_entry(self, line: str) -> None:
        entry = json.loads(line)
        assert "schema_version" in entry
        assert "timestamp" in entry
        assert "event" in entry
        assert "data" in entry

    def test_append_implementation_history(self) -> None:
        result = append_implementation_history(self.session, self.repo_root)
        assert result["status"] == "written"
        path = self.repo_root / ".agentx-init/implementation/implementation_history.jsonl"
        assert path.exists()
        self._assert_evidence_entry(path.read_text(encoding="utf-8").strip())

    def test_implementation_history_writes_evidence_file_too(self) -> None:
        append_implementation_history(self.session, self.repo_root)
        evidence_path = (
            self.repo_root / ".agentx-init/implementation/implementation_evidence.jsonl"
        )
        assert evidence_path.exists()
        self._assert_evidence_entry(evidence_path.read_text(encoding="utf-8").strip())

    def test_append_patch_application(self) -> None:
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

    def test_append_source_change_guard_result(self) -> None:
        result_obj = SourceChangeGuardResult(
            guard_id=new_id("SCG"),
            session_id=self.session.session_id,
            approved_paths=["src/main.py"],
            actual_changed_paths=["src/main.py"],
            unexpected_paths=[],
            missing_expected_paths=[],
            forbidden_paths=[],
        )
        result = append_source_change_guard_result(result_obj, self.repo_root)
        assert result["status"] == "written"
        path = (
            self.repo_root / ".agentx-init/implementation/source_change_guard_results.jsonl"
        )
        assert path.exists()

    def test_append_validation_gate_result(self) -> None:
        result_obj = ImplementationValidationGateResult(
            validation_gate_id=new_id("VG"),
            session_id=self.session.session_id,
            commands_requested=[],
            commands_allowed=[],
            commands_blocked=[],
            validation_status="PASS",
        )
        result = append_validation_gate_result(result_obj, self.repo_root)
        assert result["status"] == "written"
        path = (
            self.repo_root / ".agentx-init/implementation/validation_gate_results.jsonl"
        )
        assert path.exists()

    def test_append_rollback_record(self) -> None:
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

    def test_evidence_is_append_only(self) -> None:
        append_implementation_history(self.session, self.repo_root)
        append_implementation_history(self.session, self.repo_root)
        path = self.repo_root / ".agentx-init/implementation/implementation_history.jsonl"
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2


class TestLatestArtifact:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_write_latest_artifact(self) -> None:
        data = {"key": "value"}
        result = write_latest_artifact("test", data, self.repo_root)
        assert result["status"] == "written"
        path = self.repo_root / ".agentx-init/implementation/latest_test.json"
        assert path.exists()
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["data"] == data

    def test_latest_artifact_also_writes_evidence(self) -> None:
        write_latest_artifact("test", {"k": "v"}, self.repo_root)
        evidence_path = (
            self.repo_root / ".agentx-init/implementation/implementation_evidence.jsonl"
        )
        assert evidence_path.exists()


class TestBuildAuditEvent:
    def test_build_patch_execution_audit_event(self) -> None:
        session = ImplementationSession(
            session_id="IMP_001",
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )
        event = build_patch_execution_audit_event(
            session=session,
            event_type="SESSION_CREATED",
            decision="APPROVED",
            artifacts=["session.json"],
        )
        assert event["schema_version"] == "1.0"
        assert event["event"] == "patch_execution_audit_event"
        assert event["data"]["session_id"] == "IMP_001"
        assert event["data"]["event_type"] == "SESSION_CREATED"
        assert event["data"]["decision"] == "APPROVED"
        assert event["data"]["artifacts"] == ["session.json"]
