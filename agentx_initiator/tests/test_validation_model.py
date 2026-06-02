import pytest
from agentx_initiator.core.validation_model import ValidationRun, ValidationAllowlistEntry, ValidationManifest, ValidationAudit


def test_validation_run_defaults():
    vr = ValidationRun(run_id="r1", command="echo hi", status="PASS", returncode=0, stdout="hi", stderr="", duration_ms=10, entry_id="e1")
    assert vr.status == "PASS"


def test_validation_run_to_dict():
    vr = ValidationRun(run_id="r1", command="echo hi", status="PASS", returncode=0, stdout="hi", stderr="", duration_ms=10, entry_id="e1")
    d = vr.to_dict()
    assert d["run_id"] == "r1"
    assert d["status"] == "PASS"


def test_validation_allowlist_entry_defaults():
    e = ValidationAllowlistEntry(entry_id="e1", command_pattern="pytest", source="allowlist", category="test", max_timeout=60)
    assert e.category == "test"


def test_validation_manifest_to_dict():
    m = ValidationManifest(manifest_id="m1", report_id="r1", run_count=2, passed_count=1, failed_count=1, created_at="now")
    d = m.to_dict()
    assert d["run_count"] == 2


def test_validation_audit_defaults():
    a = ValidationAudit()
    assert a.source_component == "ValidationRunner"
