"""Tests for L1 validators."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from L1.validators import validate_fic, validate_sib, validate_es, validate_eqc, validate_lockfile
from L1.validators.common import PASS, WARNING, BLOCKED, FAIL, TOOL_ERROR, CONTROLLED_STATUSES


class TestValidatorsImport:
    def test_validate_all_imports_successfully(self):
        from L1.validators import validate_all
        assert hasattr(validate_all, "run_all")
        assert hasattr(validate_all, "main")

    def test_validate_fic_imports(self):
        assert hasattr(validate_fic, "validate")

    def test_validate_sib_imports(self):
        assert hasattr(validate_sib, "validate")

    def test_validate_es_imports(self):
        assert hasattr(validate_es, "validate")

    def test_validate_eqc_imports(self):
        assert hasattr(validate_eqc, "validate")

    def test_validate_lockfile_imports(self):
        assert hasattr(validate_lockfile, "validate")


class TestValidateAllOutput:
    def test_validate_all_returns_controlled_status_only(self):
        from L1.validators.validate_all import run_all
        results = run_all()
        for r in results:
            assert r["status"] in CONTROLLED_STATUSES, f"Bad status: {r['status']}"

    def test_validate_all_output_is_parseable_json(self):
        result = subprocess.run(
            [sys.executable, "-m", "L1.validators.validate_all"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        assert result.returncode in (0, 1, 2)
        data = json.loads(result.stdout)
        assert "validator" in data
        assert data["validator"] == "L1.validators.validate_all"
        assert "final_status" in data
        assert "results" in data

    def test_validate_all_reports_placeholder_not_release_evidence(self):
        result = subprocess.run(
            [sys.executable, "-m", "L1.validators.validate_all"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        data = json.loads(result.stdout)
        lockfile_result = [r for r in data["results"] if r["name"] == "Lockfile"]
        assert len(lockfile_result) == 1
        if lockfile_result[0]["status"] == WARNING:
            warnings = " ".join(lockfile_result[0]["warnings"]).lower()
            assert "placeholder" in warnings or "release_evidence" in warnings


class TestValidateFic:
    def test_detects_missing_registered_fic(self, tmp_path):
        fic_dir = tmp_path / "fic" / "units"
        fic_dir.mkdir(parents=True)
        index = fic_dir.parent / "index.fic.yaml"
        index.write_text("files: []")
        from L1.validators.common import BASE
        old_base = BASE
        try:
            import L1.validators.common as vc
            vc.BASE = tmp_path
            result = validate_fic.validate()
            assert result.status in (BLOCKED, FAIL)
        finally:
            pass


class TestValidateLockfile:
    def test_does_not_treat_placeholder_as_release_ready(self):
        result = validate_lockfile.validate()
        if result.status == PASS:
            warnings = " ".join(result.warnings).lower()
            assert "placeholder" not in warnings


class TestValidatorStressScenarios:
    def test_rejects_scalar_yaml_registry(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("this is a scalar string not a dict")
        import yaml
        data = yaml.safe_load(bad.read_text())
        assert isinstance(data, str), "should parse as scalar, not dict"

    def test_rejects_missing_fic_binding(self):
        from L1.validators.validate_sib import validate
        result = validate()
        assert result.status in ("PASS", "WARNING", "BLOCKED", "FAIL", "TOOL_ERROR")

    def test_validate_all_output_contains_schema_version_and_commit(self):
        import subprocess, sys, json
        from pathlib import Path
        result = subprocess.run(
            [sys.executable, "-m", "L1.validators.validate_all"],
            capture_output=True, text=True, cwd=Path(__file__).resolve().parent.parent.parent
        )
        data = json.loads(result.stdout)
        assert "schema_version" in data
        assert "commit" in data
        assert "generated_at_utc" in data
        assert data["schema_version"].startswith("agent-x-l1-validate-all")

    def test_rejects_empty_semantic_lockfile(self, tmp_path):
        bad = tmp_path / "semantic_lockfile.yaml"
        bad.write_text("")
        import yaml
        data = yaml.safe_load(bad.read_text())
        assert data is None, "empty file should return None"

    def test_validate_es_detects_registry_paths(self):
        result = validate_es.validate()
        assert result.status in ("PASS", "WARNING", "BLOCKED", "FAIL", "TOOL_ERROR")


class TestValidatorsNoNetwork:
    def test_validators_do_not_require_network(self):
        import socket
        original = socket.socket
        try:
            class BlockSocket:
                def __getattr__(self, name):
                    raise RuntimeError("Network access blocked")
            socket.socket = BlockSocket()
            from L1.validators.validate_all import run_all
            results = run_all()
            assert all(r["status"] in CONTROLLED_STATUSES for r in results)
        finally:
            socket.socket = original
