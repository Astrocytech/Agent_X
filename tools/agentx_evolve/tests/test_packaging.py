import pytest
from agentx_evolve.packaging.packaging_checker import (
    PackagingCheckResult, PackagingDistributionCheck, PackagingChecker,
    PKG_SCHEMA_VERSION, PKG_CHECK_PASS, PKG_CHECK_FAIL, PKG_CHECK_WARN,
    ALL_PACKAGING_CHECK_RESULTS,
    PKG_DEP_LOCAL_MODEL, PKG_DEP_MCP, PKG_DEP_GIT, PKG_DEP_DEV, PKG_DEP_HOSTED_MODEL,
    ALL_PACKAGING_DEP_GROUPS,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_pkg_schema_version():
    assert PKG_SCHEMA_VERSION == "1.0"

def test_all_packaging_check_results():
    assert PKG_CHECK_PASS in ALL_PACKAGING_CHECK_RESULTS
    assert PKG_CHECK_FAIL in ALL_PACKAGING_CHECK_RESULTS
    assert PKG_CHECK_WARN in ALL_PACKAGING_CHECK_RESULTS
    assert len(ALL_PACKAGING_CHECK_RESULTS) == 3

def test_all_packaging_dep_groups():
    assert PKG_DEP_LOCAL_MODEL in ALL_PACKAGING_DEP_GROUPS
    assert PKG_DEP_MCP in ALL_PACKAGING_DEP_GROUPS
    assert PKG_DEP_GIT in ALL_PACKAGING_DEP_GROUPS
    assert PKG_DEP_DEV in ALL_PACKAGING_DEP_GROUPS
    assert PKG_DEP_HOSTED_MODEL in ALL_PACKAGING_DEP_GROUPS
    assert len(ALL_PACKAGING_DEP_GROUPS) == 5

# ---------------------------------------------------------------------------
# PackagingCheckResult
# ---------------------------------------------------------------------------

def test_packaging_check_result_defaults():
    r = PackagingCheckResult()
    assert r.check_name == ""
    assert r.status == PKG_CHECK_PASS
    assert r.details == ""

def test_packaging_check_result_custom():
    r = PackagingCheckResult(check_name="fresh_clone_install", status=PKG_CHECK_FAIL,
                             details="Install failed")
    assert r.check_name == "fresh_clone_install"
    assert r.status == PKG_CHECK_FAIL
    assert r.details == "Install failed"

def test_packaging_check_result_to_dict():
    r = PackagingCheckResult(check_name="test", status=PKG_CHECK_WARN)
    d = r.to_dict()
    assert d["check_name"] == "test"
    assert d["status"] == "WARN"

# ---------------------------------------------------------------------------
# PackagingDistributionCheck
# ---------------------------------------------------------------------------

def test_packaging_distribution_check_defaults():
    c = PackagingDistributionCheck()
    assert c.schema_version == "1.0"
    assert c.check_id == ""
    assert c.fresh_clone_install == PKG_CHECK_PASS
    assert c.optional_dependencies == PKG_CHECK_PASS
    assert c.base_install_no_gpu == PKG_CHECK_PASS
    assert c.commands_available == []
    assert c.dep_groups_defined == []

def test_packaging_distribution_check_custom():
    c = PackagingDistributionCheck(
        check_id="pkg_001",
        fresh_clone_install=PKG_CHECK_FAIL,
        commands_available=["agentx-init", "agentx-patch"],
        dep_groups_defined=["local-model", "git"],
    )
    assert c.check_id == "pkg_001"
    assert c.fresh_clone_install == PKG_CHECK_FAIL
    assert c.commands_available == ["agentx-init", "agentx-patch"]

def test_packaging_distribution_check_all_passed():
    c = PackagingDistributionCheck(fresh_clone_install=PKG_CHECK_PASS,
                                    optional_dependencies=PKG_CHECK_PASS,
                                    base_install_no_gpu=PKG_CHECK_PASS)
    assert c.all_passed() is True

def test_packaging_distribution_check_not_all_passed():
    c = PackagingDistributionCheck(fresh_clone_install=PKG_CHECK_FAIL)
    assert c.all_passed() is False

def test_packaging_distribution_check_to_dict():
    c = PackagingDistributionCheck(check_id="pkg_001")
    d = c.to_dict()
    assert d["check_id"] == "pkg_001"

# ---------------------------------------------------------------------------
# PackagingChecker
# ---------------------------------------------------------------------------

def test_packaging_checker_defaults():
    checker = PackagingChecker()
    assert checker.list_checks() == []

def test_packaging_checker_run_check_defaults():
    checker = PackagingChecker()
    c = checker.run_check()
    assert c.check_id.startswith("pkg-")
    assert c.checked_at != ""
    assert c.fresh_clone_install == PKG_CHECK_PASS
    assert c.commands_available == ["agentx-init", "agentx-patch", "agentx-evolve"]
    assert len(c.dep_groups_defined) == 5
    assert len(c.checks) == 3 + 3 + 5

def test_packaging_checker_run_check_custom():
    checker = PackagingChecker()
    c = checker.run_check(
        commands_available=["agentx-evolve"],
        dep_groups_defined=["local-model"],
        fresh_clone_install=PKG_CHECK_FAIL,
    )
    assert c.fresh_clone_install == PKG_CHECK_FAIL
    assert c.optional_dependencies == PKG_CHECK_PASS
    assert c.base_install_no_gpu == PKG_CHECK_PASS

def test_packaging_checker_get_check():
    checker = PackagingChecker()
    c = checker.run_check()
    assert checker.get_check(c.check_id) is c

def test_packaging_checker_get_nonexistent():
    checker = PackagingChecker()
    assert checker.get_check("nonexistent") is None

def test_packaging_checker_list_checks():
    checker = PackagingChecker()
    checker.run_check()
    checker.run_check()
    assert len(checker.list_checks()) == 2

def test_packaging_checker_clear():
    checker = PackagingChecker()
    checker.run_check()
    checker.clear()
    assert checker.list_checks() == []
