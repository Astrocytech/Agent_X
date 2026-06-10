import json, os, sys, tempfile
from pathlib import Path
from agentx_evolve.recovery.failure_models import (
    FailureRecord, make_failure_record, to_dict,
    SEVERITY_HIGH, SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_CRITICAL,
)
from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession, RollbackSnapshot, RollbackRecord,
    SESSION_STATUS_ROLLED_BACK,
)
from agentx_evolve.patch_execution.rollback_manager import create_rollback_snapshot, rollback_session
from agentx_evolve.recovery.failure_evidence import append_failure_record


class TestFailureRollbackFlow:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.repo_root = self.tmpdir / "repo"
        self.repo_root.mkdir()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_validation_failure_triggers_rollback(self):
        failure = make_failure_record(
            failure_class="VALIDATION_FAILED",
            message="Test validation failure",
            severity=SEVERITY_HIGH,
            source_layer="test",
        )
        assert failure.failure_class == "VALIDATION_FAILED"
        assert failure.severity == SEVERITY_HIGH
        assert failure.requires_recovery

    def test_rollback_evidence_is_created(self):
        session = ImplementationSession(session_id="rb-session-1")
        target = self.repo_root / "src"
        target.mkdir(parents=True)
        test_file = target / "evidence_test.txt"
        test_file.write_text("original")
        snapshot = create_rollback_snapshot(session, self.repo_root, ["src/evidence_test.txt"])
        test_file.write_text("modified")
        record = rollback_session(session, snapshot, self.repo_root, "VALIDATION_FAILED")
        assert record.status == "ROLLED_BACK"
        assert "src/evidence_test.txt" in record.restored_files

    def test_failure_records_are_schema_valid(self):
        for severity in (SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL):
            failure = make_failure_record(
                failure_class="SCHEMA_VALIDATION_FAILED",
                message=f"Test {severity} failure",
                severity=severity,
            )
            d = to_dict(failure)
            assert d["failure_class"] == "SCHEMA_VALIDATION_FAILED"
            assert d["severity"] == severity
            assert d["schema_version"] == "1.0"
