import json
import os
import pytest
from pathlib import Path
from agentx_evolve.acceptance.acceptance import (
    AcceptanceCheck, AcceptanceCheckResult, AcceptanceReport,
    AcceptanceReportHash,
    AC_SCHEMA_VERSION, AC_SCHEMA_ID,
    AC_CHECK_PASS, AC_CHECK_FAIL, AC_CHECK_SKIP,
    ALL_ACCEPTANCE_CHECK_RESULTS,
    canonical_json, sha256_dict,
    write_json_atomic, append_jsonl,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_ac_schema_version():
    assert AC_SCHEMA_VERSION == "1.0"

def test_ac_schema_id():
    assert AC_SCHEMA_ID == "acceptance_check_result.schema.json"

def test_all_acceptance_check_results():
    assert AC_CHECK_PASS in ALL_ACCEPTANCE_CHECK_RESULTS
    assert AC_CHECK_FAIL in ALL_ACCEPTANCE_CHECK_RESULTS
    assert AC_CHECK_SKIP in ALL_ACCEPTANCE_CHECK_RESULTS
    assert len(ALL_ACCEPTANCE_CHECK_RESULTS) == 3

# ---------------------------------------------------------------------------
# AcceptanceCheckResult
# ---------------------------------------------------------------------------

def test_acceptance_check_result_defaults():
    r = AcceptanceCheckResult()
    assert r.check_name == ""
    assert r.status == AC_CHECK_SKIP
    assert r.details == ""

def test_acceptance_check_result_custom():
    r = AcceptanceCheckResult(check_name="fresh_clone_install", status=AC_CHECK_PASS,
                               details="Install works")
    assert r.check_name == "fresh_clone_install"
    assert r.status == AC_CHECK_PASS
    assert r.details == "Install works"

def test_acceptance_check_result_to_dict():
    r = AcceptanceCheckResult(check_name="test", status=AC_CHECK_FAIL)
    d = r.to_dict()
    assert d["check_name"] == "test"
    assert d["status"] == "FAIL"

# ---------------------------------------------------------------------------
# AcceptanceReport
# ---------------------------------------------------------------------------

def test_acceptance_report_defaults():
    r = AcceptanceReport()
    assert r.schema_version == "1.0"
    assert r.schema_id == "acceptance_check_result.schema.json"
    assert r.report_id == ""
    assert r.checks == []
    assert r.total == 0
    assert r.passed == 0
    assert r.failed == 0
    assert r.skipped == 0
    assert r.all_passed is False

def test_acceptance_report_custom():
    r = AcceptanceReport(report_id="ac_001", total=5, passed=3, failed=1, skipped=1)
    assert r.report_id == "ac_001"
    assert r.total == 5
    assert r.passed == 3
    assert r.failed == 1
    assert r.skipped == 1

def test_acceptance_report_to_dict():
    r = AcceptanceReport(report_id="ac_001")
    d = r.to_dict()
    assert d["report_id"] == "ac_001"
    assert d["schema_id"] == "acceptance_check_result.schema.json"

# ---------------------------------------------------------------------------
# AcceptanceReportHash
# ---------------------------------------------------------------------------

def test_acceptance_report_hash_defaults():
    report = AcceptanceReport(report_id="ac_001")
    rh = AcceptanceReportHash(report=report)
    assert rh.hash
    assert len(rh.hash) == 64

def test_acceptance_report_hash_to_dict():
    report = AcceptanceReport(report_id="ac_001")
    rh = AcceptanceReportHash(report=report)
    d = rh.to_dict()
    assert d["report_id"] == "ac_001"
    assert "_hash" in d
    assert len(d["_hash"]) == 64

def test_acceptance_report_hash_deterministic():
    report = AcceptanceReport(report_id="ac_001")
    rh1 = AcceptanceReportHash(report=report)
    rh2 = AcceptanceReportHash(report=report)
    assert rh1.hash == rh2.hash

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def test_canonical_json():
    d = {"b": 2, "a": 1}
    result = canonical_json(d)
    assert result == '{"a":1,"b":2}'

def test_sha256_dict():
    d = {"a": 1, "b": 2}
    h = sha256_dict(d)
    assert len(h) == 64
    assert sha256_dict(d) == sha256_dict(dict(d))

def test_write_json_atomic(tmp_path: Path):
    data = {"key": "value", "num": 42}
    dest = tmp_path / "test.json"
    write_json_atomic(dest, data)
    assert dest.exists()
    with open(dest) as f:
        loaded = json.load(f)
    assert loaded["key"] == "value"
    assert loaded["num"] == 42

def test_append_jsonl(tmp_path: Path):
    path = tmp_path / "test.jsonl"
    append_jsonl(path, {"a": 1})
    append_jsonl(path, {"b": 2})
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"a": 1}
    assert json.loads(lines[1]) == {"b": 2}

# ---------------------------------------------------------------------------
# AcceptanceCheck
# ---------------------------------------------------------------------------

def test_acceptance_check_defaults():
    check = AcceptanceCheck()
    assert len(check._check_names) == 19
    assert "fresh_clone_install" in check._check_names
    assert "backup_restore" in check._check_names
    assert "controlled_degradation" in check._check_names

def test_acceptance_check_run_all():
    check = AcceptanceCheck()
    report = check.run_all()
    assert report.report_id.startswith("ac-")
    assert report.total == 19
    assert report.skipped == 0
    assert len(report.checks) == 19

def test_acceptance_report_all_passed():
    report = AcceptanceReport(
        report_id="ac-test",
        checked_at="2026-01-01T00:00:00+00:00",
        checks=[
            AcceptanceCheckResult(check_name="a", status=AC_CHECK_PASS),
            AcceptanceCheckResult(check_name="b", status=AC_CHECK_PASS),
        ],
    )
    report.total = 2
    report.passed = 2
    report.failed = 0
    report.skipped = 0
    report.all_passed = report.failed == 0
    assert report.all_passed is True
    assert report.failed == 0

def test_acceptance_check_set_result():
    check = AcceptanceCheck()
    check.set_result("fresh_clone_install", AC_CHECK_PASS, details="Installed successfully")
    result = check.get_result("fresh_clone_install")
    assert result is not None
    assert result.status == AC_CHECK_PASS
    assert result.details == "Installed successfully"

def test_acceptance_check_set_result_new_check():
    check = AcceptanceCheck()
    check.set_result("custom_check", AC_CHECK_PASS)
    result = check.get_result("custom_check")
    assert result is not None
    assert result.check_name == "custom_check"
    assert "custom_check" in check._check_names

def test_acceptance_check_get_nonexistent():
    check = AcceptanceCheck()
    assert check.get_result("nonexistent") is None

def test_acceptance_check_all_passed_empty():
    check = AcceptanceCheck()
    assert check.all_passed() is False

def test_acceptance_check_all_passed_true():
    check = AcceptanceCheck()
    check.set_result("check_1", AC_CHECK_PASS)
    check.set_result("check_2", AC_CHECK_PASS)
    assert check.all_passed() is True

def test_acceptance_check_all_passed_false():
    check = AcceptanceCheck()
    check.set_result("check_1", AC_CHECK_PASS)
    check.set_result("check_2", AC_CHECK_FAIL)
    assert check.all_passed() is False

def test_acceptance_check_summary():
    check = AcceptanceCheck()
    check.set_result("check_1", AC_CHECK_PASS)
    check.set_result("check_2", AC_CHECK_FAIL)
    check.set_result("check_3", AC_CHECK_SKIP)
    s = check.summary()
    assert s["total"] == 3
    assert s["passed"] == 1
    assert s["failed"] == 1
    assert s["skipped"] == 1
    assert s["all_passed"] is False

def test_acceptance_check_summary_all_pass():
    check = AcceptanceCheck()
    check.set_result("check_1", AC_CHECK_PASS)
    check.set_result("check_2", AC_CHECK_PASS)
    s = check.summary()
    assert s["all_passed"] is True

def test_generate_report_returns_valid():
    check = AcceptanceCheck()
    check.set_result("fresh_clone_install", AC_CHECK_PASS)
    check.set_result("rollback", AC_CHECK_FAIL)
    report = check.generate_report()
    assert report.report_id.startswith("ac-")
    assert report.total == 19
    assert report.passed >= 1
    assert report.failed >= 1
    for c in report.checks:
        if c.check_name == "fresh_clone_install":
            assert c.status == AC_CHECK_PASS
        elif c.check_name == "rollback":
            assert c.status == AC_CHECK_FAIL

def test_acceptance_check_all_check_names_present():
    check = AcceptanceCheck()
    expected = [
        "fresh_clone_install", "initiator_commands", "patch_execution",
        "rollback", "source_guard", "llm_worker_output", "orchestrator_session",
        "human_review", "promotion_gate", "audit_memory_graph",
        "no_l0_mutation", "no_uncontrolled_shell", "no_network_default",
        "small_model_profile", "schema_validation", "tool_protocol",
        "prompt_contracts", "backup_restore", "controlled_degradation",
    ]
    for name in expected:
        assert name in check._check_names, f"Missing check: {name}"
    assert len(check._check_names) == len(expected)

# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def test_validate_report_schema_valid():
    check = AcceptanceCheck()
    report = check.run_all()
    errors = check.validate_report_schema(report)
    assert errors == [], f"Schema validation errors: {errors}"

# ---------------------------------------------------------------------------
# File I/O integration
# ---------------------------------------------------------------------------

def test_write_acceptance_report_creates_file(tmp_path: Path):
    check = AcceptanceCheck()
    report = check.run_all()
    base = tmp_path / "acceptance"
    path = check.write_acceptance_report(report, base=base)
    assert path.exists()
    with open(path) as f:
        data = json.load(f)
    assert data["report_id"] == report.report_id
    assert data["total"] == 19

def test_append_acceptance_history_appends(tmp_path: Path):
    check = AcceptanceCheck()
    report = check.run_all()
    base = tmp_path / "acceptance"
    path = check.append_acceptance_history(report, base=base)
    assert path.exists()
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 1
    # Append a second report
    check.append_acceptance_history(report, base=base)
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 2

# ---------------------------------------------------------------------------
# Lock
# ---------------------------------------------------------------------------

def test_acceptance_lock_acquire_release(tmp_path: Path):
    check = AcceptanceCheck()
    base = tmp_path / "acceptance"
    with check.acquire_acceptance_lock(base=base) as lock_path:
        assert lock_path.exists()
    assert not lock_path.exists()
