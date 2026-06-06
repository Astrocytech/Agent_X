import pytest
from agentx_evolve.security.security_models import (
    SecurityViolation, SV_PATH_ESCAPE, SV_SUBPROCESS, SV_REDACTION_FAIL
)


def test_violation_records_correct_type():
    v = SecurityViolation(violation_id="sv-1", violation_type=SV_PATH_ESCAPE, target="/etc/passwd")
    assert v.violation_id == "sv-1"
    assert v.violation_type == SV_PATH_ESCAPE
    assert v.target == "/etc/passwd"


def test_violation_serializes_to_dict():
    v = SecurityViolation(
        violation_id="sv-2",
        violation_type=SV_SUBPROCESS,
        reason="unauthorized command",
        severity="high",
    )
    d = v.to_dict()
    assert d["violation_id"] == "sv-2"
    assert d["violation_type"] == SV_SUBPROCESS
    assert d["reason"] == "unauthorized command"
    assert d["severity"] == "high"


def test_redaction_fail_violation():
    v = SecurityViolation(violation_id="sv-3", violation_type=SV_REDACTION_FAIL)
    assert v.violation_type == SV_REDACTION_FAIL
    assert v.severity == "medium"


def test_violation_defaults():
    v = SecurityViolation()
    assert v.violation_id == ""
    assert v.source_component == "Security"


def test_violation_all_types():
    for vt in [SV_PATH_ESCAPE, SV_SUBPROCESS, SV_REDACTION_FAIL]:
        v = SecurityViolation(violation_id=f"sv-{vt}", violation_type=vt)
        assert v.violation_type == vt
