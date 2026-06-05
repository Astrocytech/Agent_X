import pytest
from agentx_evolve.acceptance.acceptance import (
    AcceptanceCheck, AcceptanceCheckResult, AcceptanceReport,
    AC_SCHEMA_VERSION, AC_CHECK_PASS, AC_CHECK_FAIL, AC_CHECK_SKIP,
    ALL_ACCEPTANCE_CHECK_RESULTS,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_ac_schema_version():
    assert AC_SCHEMA_VERSION == "1.0"

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
    assert report.passed == 0
    assert report.failed == 0
    assert report.skipped == 19
    assert report.all_passed is True  # no failures
    assert len(report.checks) == 19

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

def test_acceptance_check_generate_report():
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
