import json
from pathlib import Path

import pytest

from agentx_evolve.packaging.packaging_checker import (
    PackagingCheckResult, PackagingDistributionCheck, PackagingChecker,
    PackagingResultHash,
    PKG_SCHEMA_VERSION, PKG_SCHEMA_ID, PKG_CHECK_PASS, PKG_CHECK_FAIL, PKG_CHECK_WARN,
    ALL_PACKAGING_CHECK_RESULTS,
    PKG_DEP_LOCAL_MODEL, PKG_DEP_MCP, PKG_DEP_GIT, PKG_DEP_DEV, PKG_DEP_HOSTED_MODEL,
    ALL_PACKAGING_DEP_GROUPS,
    canonical_json, sha256_dict, packaging_runs_dir,
)


class TestConstants:
    def test_pkg_schema_version(self):
        assert PKG_SCHEMA_VERSION == "1.0"

    def test_pkg_schema_id(self):
        assert PKG_SCHEMA_ID == "packaging_distribution_check.schema.json"

    def test_all_packaging_check_results(self):
        assert PKG_CHECK_PASS in ALL_PACKAGING_CHECK_RESULTS
        assert PKG_CHECK_FAIL in ALL_PACKAGING_CHECK_RESULTS
        assert PKG_CHECK_WARN in ALL_PACKAGING_CHECK_RESULTS
        assert len(ALL_PACKAGING_CHECK_RESULTS) == 3

    def test_all_packaging_dep_groups(self):
        assert PKG_DEP_LOCAL_MODEL in ALL_PACKAGING_DEP_GROUPS
        assert PKG_DEP_MCP in ALL_PACKAGING_DEP_GROUPS
        assert PKG_DEP_GIT in ALL_PACKAGING_DEP_GROUPS
        assert PKG_DEP_DEV in ALL_PACKAGING_DEP_GROUPS
        assert PKG_DEP_HOSTED_MODEL in ALL_PACKAGING_DEP_GROUPS
        assert len(ALL_PACKAGING_DEP_GROUPS) == 5


class TestCanonicalJsonAndHash:
    def test_canonical_json_sorts_keys(self):
        result = canonical_json({"b": 2, "a": 1})
        assert result == '{"a":1,"b":2}'

    def test_sha256_dict_is_deterministic(self):
        data = {"check": "test", "value": 42}
        assert sha256_dict(data) == sha256_dict(data)

    def test_sha256_dict_different_data(self):
        assert sha256_dict({"a": 1}) != sha256_dict({"a": 2})


class TestPackagingResultHash:
    def test_defaults(self):
        h = PackagingResultHash()
        assert h.hash_value == ""
        assert h.algorithm == "sha256"

    def test_compute_returns_hash(self):
        h = PackagingResultHash()
        result = h.compute({"a": 1})
        assert isinstance(result, str)
        assert len(result) == 64
        assert h.hash_value == result

    def test_compute_deterministic(self):
        h = PackagingResultHash()
        assert h.compute({"a": 1}) == h.compute({"a": 1})


class TestPackagingCheckResult:
    def test_packaging_check_result_defaults(self):
        r = PackagingCheckResult()
        assert r.check_name == ""
        assert r.status == PKG_CHECK_PASS
        assert r.details == ""

    def test_packaging_check_result_custom(self):
        r = PackagingCheckResult(check_name="fresh_clone_install", status=PKG_CHECK_FAIL,
                                 details="Install failed")
        assert r.check_name == "fresh_clone_install"
        assert r.status == PKG_CHECK_FAIL
        assert r.details == "Install failed"

    def test_packaging_check_result_to_dict(self):
        r = PackagingCheckResult(check_name="test", status=PKG_CHECK_WARN)
        d = r.to_dict()
        assert d["check_name"] == "test"
        assert d["status"] == "WARN"


class TestPackagingDistributionCheck:
    def test_packaging_distribution_check_defaults(self):
        c = PackagingDistributionCheck()
        assert c.schema_version == "1.0"
        assert c.schema_id == PKG_SCHEMA_ID
        assert c.check_id == ""
        assert c.fresh_clone_install == PKG_CHECK_PASS
        assert c.optional_dependencies == PKG_CHECK_PASS
        assert c.base_install_no_gpu == PKG_CHECK_PASS
        assert c.commands_available == []
        assert c.dep_groups_defined == []
        assert c.result_hash == ""

    def test_packaging_distribution_check_custom(self):
        c = PackagingDistributionCheck(
            check_id="pkg_001",
            fresh_clone_install=PKG_CHECK_FAIL,
            commands_available=["agentx-init", "agentx-patch"],
            dep_groups_defined=["local-model", "git"],
        )
        assert c.check_id == "pkg_001"
        assert c.fresh_clone_install == PKG_CHECK_FAIL
        assert c.commands_available == ["agentx-init", "agentx-patch"]

    def test_all_passed_true_when_all_pass(self):
        c = PackagingDistributionCheck(fresh_clone_install=PKG_CHECK_PASS,
                                        optional_dependencies=PKG_CHECK_PASS,
                                        base_install_no_gpu=PKG_CHECK_PASS)
        assert c.all_passed() is True

    def test_all_passed_false_when_one_fails(self):
        c = PackagingDistributionCheck(fresh_clone_install=PKG_CHECK_FAIL)
        assert c.all_passed() is False

    def test_all_passed_false_when_one_warns(self):
        c = PackagingDistributionCheck(optional_dependencies=PKG_CHECK_WARN)
        assert c.all_passed() is False

    def test_to_dict_includes_schema_id_and_hash(self):
        c = PackagingDistributionCheck(check_id="pkg_001")
        d = c.to_dict()
        assert d["check_id"] == "pkg_001"
        assert d["schema_id"] == PKG_SCHEMA_ID
        assert "result_hash" in d

    def test_validate_schema_valid(self):
        data = {
            "schema_version": "1.0",
            "schema_id": "packaging_distribution_check.schema.json",
            "check_id": "pkg-abc",
            "fresh_clone_install": "PASS",
            "optional_dependencies": "PASS",
            "base_install_no_gpu": "PASS",
            "commands_available": ["agentx-init"],
            "dep_groups_defined": ["local-model"],
            "checks": [{"check_name": "test", "status": "PASS"}],
            "checked_at": "2025-01-01T00:00:00",
            "warnings": [],
            "errors": [],
        }
        errs = PackagingDistributionCheck.validate_schema(data)
        assert errs == []

    def test_validate_schema_missing_field(self):
        data = {"check_id": "pkg-abc"}
        errs = PackagingDistributionCheck.validate_schema(data)
        assert any("schema_version" in e for e in errs)
        assert any("fresh_clone_install" in e for e in errs)

    def test_validate_schema_bad_status(self):
        data = {
            "schema_version": "1.0",
            "schema_id": "packaging_distribution_check.schema.json",
            "check_id": "pkg-abc",
            "fresh_clone_install": "INVALID",
            "base_install_no_gpu": "PASS",
            "commands_available": [],
            "dep_groups_defined": [],
            "checks": [],
            "checked_at": "",
            "warnings": [],
            "errors": [],
        }
        errs = PackagingDistributionCheck.validate_schema(data)
        assert any("fresh_clone_install" in e for e in errs)

    def test_validate_schema_bad_schema_version(self):
        data = {
            "schema_version": "2.0",
            "schema_id": "packaging_distribution_check.schema.json",
            "check_id": "pkg-abc",
            "fresh_clone_install": "PASS",
            "base_install_no_gpu": "PASS",
            "commands_available": [],
            "dep_groups_defined": [],
            "checks": [],
            "checked_at": "",
            "warnings": [],
            "errors": [],
        }
        errs = PackagingDistributionCheck.validate_schema(data)
        assert any("schema_version" in e for e in errs)


class TestPackagingChecker:
    def test_packaging_checker_defaults(self):
        checker = PackagingChecker()
        assert checker.list_checks() == []

    def test_run_check_returns_valid(self):
        checker = PackagingChecker()
        c = checker.run_check()
        assert c.check_id.startswith("pkg-")
        assert c.checked_at != ""
        assert c.fresh_clone_install == PKG_CHECK_PASS
        assert c.optional_dependencies == PKG_CHECK_PASS
        assert c.base_install_no_gpu == PKG_CHECK_PASS
        assert len(c.commands_available) > 0
        assert len(c.dep_groups_defined) > 0
        assert len(c.checks) >= 3
        assert c.schema_id == PKG_SCHEMA_ID
        assert c.result_hash != ""

    def test_run_check_custom(self):
        checker = PackagingChecker()
        c = checker.run_check(
            commands_available=["agentx-evolve"],
            dep_groups_defined=["local-model"],
            fresh_clone_install=PKG_CHECK_FAIL,
        )
        assert c.fresh_clone_install == PKG_CHECK_FAIL
        assert c.optional_dependencies == PKG_CHECK_PASS
        assert c.base_install_no_gpu == PKG_CHECK_PASS

    def test_get_check(self):
        checker = PackagingChecker()
        c = checker.run_check()
        assert checker.get_check(c.check_id) is c

    def test_get_nonexistent(self):
        checker = PackagingChecker()
        assert checker.get_check("nonexistent") is None

    def test_list_checks(self):
        checker = PackagingChecker()
        checker.run_check()
        checker.run_check()
        assert len(checker.list_checks()) == 2

    def test_clear(self):
        checker = PackagingChecker()
        checker.run_check()
        checker.clear()
        assert checker.list_checks() == []

    def test_result_hash_changes_with_status(self):
        checker = PackagingChecker()
        c1 = checker.run_check(fresh_clone_install=PKG_CHECK_PASS)
        c2 = checker.run_check(fresh_clone_install=PKG_CHECK_FAIL)
        assert c1.result_hash != c2.result_hash


class TestPersistence:
    def test_write_check_report_creates_file(self, tmp_path: Path):
        checker = PackagingChecker()
        check = checker.run_check()
        result_path = checker.write_check_report(check, tmp_path)
        assert result_path.exists()
        data = json.loads(result_path.read_text())
        assert data["check_id"] == check.check_id

    def test_append_check_history_appends(self, tmp_path: Path):
        checker = PackagingChecker()
        check = checker.run_check()
        history_path = checker.append_check_history(check, tmp_path)
        assert history_path.exists()
        lines = history_path.read_text().strip().split("\n")
        assert len(lines) >= 1
        last = json.loads(lines[-1])
        assert last["check_id"] == check.check_id

    def test_run_check_with_repo_root_persists(self, tmp_path: Path):
        checker = PackagingChecker()
        check = checker.run_check(repo_root=tmp_path)
        report_path = packaging_runs_dir(tmp_path) / "packaging_check_report.json"
        assert report_path.exists()
        history_path = packaging_runs_dir(tmp_path) / "packaging_history.jsonl"
        assert history_path.exists()

    def test_packaging_lock_acquire_release(self, tmp_path: Path):
        checker = PackagingChecker()
        lock = checker.acquire_packaging_lock(tmp_path)
        assert lock["acquired"] is True
        checker.release_packaging_lock(lock, tmp_path)
        lock_path = packaging_runs_dir(tmp_path) / ".packaging.lock"
        assert not lock_path.exists()

    def test_lock_timeout_raises(self, tmp_path: Path):
        checker = PackagingChecker()
        lock1 = checker.acquire_packaging_lock(tmp_path)
        with pytest.raises(TimeoutError):
            checker.acquire_packaging_lock(tmp_path, timeout_seconds=0)
        checker.release_packaging_lock(lock1, tmp_path)

    def test_packaging_runs_dir(self):
        p = packaging_runs_dir(Path("/repo"))
        assert p == Path("/repo/.agentx-init/packaging")
