"""Negative tests for Functional Runtime MVP validators.

Each test corrupts or removes evidence and verifies the relevant validator
rejects it.  Tests use a temp directory to avoid mutating real reports.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPORT_DIR = Path(".agentx-init/reports")
ROOT = Path(__file__).resolve().parent.parent.parent.parent
VALIDATORS_DIR = ROOT / "tools/agentx_evolve/validators"


def _run_validator(name: str, report_dir: Path) -> int:
    root = Path(__file__).resolve().parent.parent.parent.parent
    pythonpath = "L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools"
    abs_pythonpath = ":".join(str(root / p) for p in pythonpath.split(":"))
    env = {**os.environ, "PYTHONPATH": abs_pythonpath}
    if (root / ".git").is_dir():
        env["GIT_DIR"] = str(root / ".git")
    r = subprocess.run(
        [sys.executable, str(VALIDATORS_DIR / f"{name}.py"),
         "--report-dir", str(report_dir)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    return r.returncode


def _copy_reports(dst: Path) -> None:
    """Prepare temp workspace with real reports or minimal stubs."""
    (dst / ".agentx-init").mkdir(parents=True, exist_ok=True)
    dst_reports = dst / ".agentx-init" / "reports"
    dst_reports.mkdir(parents=True, exist_ok=True)
    if REPORT_DIR.exists():
        for f in REPORT_DIR.glob("*"):
            if f.is_file():
                (dst_reports / f.name).write_bytes(f.read_bytes())
    # Create minimal stubs for required reports that may not exist at test time
    stub_matrix = dst_reports / "functional_runtime_mvp_acceptance_matrix.json"
    if not stub_matrix.exists():
        stub_matrix.write_text('{"rows": [{"component": "test", "status": "PASS", "evidence_refs": [{"path": "' + str(dst_reports / "placeholder.json") + '", "type": "test"}]}]}', encoding="utf-8")
    os.chdir(dst)


def _cleanup(dst: Path) -> None:
    os.chdir(str(ROOT))


@pytest.fixture
def temp_reports() -> Path:
    dst = Path(tempfile.mkdtemp(prefix="mvp_validator_test_"))
    _copy_reports(dst)
    yield dst / ".agentx-init" / "reports"
    _cleanup(dst)
    shutil.rmtree(dst, ignore_errors=True)


def _load_matrix(report_dir: Path) -> dict:
    p = report_dir / "functional_runtime_mvp_acceptance_matrix.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _write_matrix(report_dir: Path, data: dict) -> None:
    p = report_dir / "functional_runtime_mvp_acceptance_matrix.json"
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


class TestValidatorNegativeTests:
    """Validators must reject corrupted, missing, stale, or contradictory evidence."""

    def test_acceptance_matrix_rejects_pass_without_evidence(self, temp_reports: Path) -> None:
        matrix = _load_matrix(temp_reports)
        for row in matrix.get("rows", []):
            row["status"] = "PASS"
            row.pop("evidence_refs", None)
        _write_matrix(temp_reports, matrix)
        rc = _run_validator("validate_functional_runtime_mvp_reports", temp_reports)
        assert rc != 0, "Validator should reject PASS row without evidence_refs"

    def test_acceptance_matrix_rejects_missing_evidence_file(self, temp_reports: Path) -> None:
        matrix = _load_matrix(temp_reports)
        rows = matrix.get("rows", [])
        if rows:
            rows[0]["evidence_refs"] = [{"path": "/nonexistent/file.json", "type": "test", "hash": ""}]
        _write_matrix(temp_reports, matrix)
        rc = _run_validator("validate_functional_runtime_mvp_reports", temp_reports)
        assert rc != 0, "Validator should reject ref to missing evidence file"

    def test_acceptance_matrix_rejects_missing_required_row(self, temp_reports: Path) -> None:
        # Create a matrix with zero rows
        _write_matrix(temp_reports, {"generated_at": "now", "rows": []})
        rc = _run_validator("validate_functional_runtime_mvp_reports", temp_reports)
        assert rc != 0, "Validator should reject empty acceptance matrix"

    def test_replay_report_rejects_mismatch(self, temp_reports: Path) -> None:
        p = temp_reports / "functional_runtime_mvp_replay_report.json"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data:
                    item["replay_verdict"] = "FAIL"
            elif isinstance(data, dict) and "rows" in data:
                for item in data["rows"]:
                    item["replay_verdict"] = "FAIL"
            p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        rc = _run_validator("validate_functional_runtime_mvp_replay", temp_reports)
        assert rc != 0, "Validator should reject replay verdict mismatch"

    def test_command_transcript_rejects_static_success(self, temp_reports: Path) -> None:
        p = temp_reports / "functional_runtime_mvp_command_transcript.json"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for cmd in data:
                    cmd["source"] = "static"
                p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        rc = _run_validator("validate_functional_runtime_mvp_transcript", temp_reports)
        assert rc != 0, "Validator should reject static transcript"

    def test_traceability_rejects_unmapped_requirement(self, temp_reports: Path) -> None:
        # Remove all rows from traceability matrix
        p = temp_reports / "functional_runtime_mvp_requirement_traceability_matrix.json"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            data["rows"] = []
            p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        rc = _run_validator("validate_functional_runtime_mvp_traceability", temp_reports)
        assert rc != 0, "Validator should reject empty traceability matrix"

    def test_gap_discovery_rejects_unclassified_gap(self, temp_reports: Path) -> None:
        p = temp_reports / "functional_runtime_mvp_gap_discovery_report.json"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            data["known_gaps_confirmed"] = []
            data["new_gaps_discovered"] = []
            p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        rc = _run_validator("validate_functional_runtime_mvp_gap_discovery", temp_reports)
        assert rc != 0, "Validator should reject gap report with no gaps"

    def test_validator_rejects_corrupt_json(self, temp_reports: Path) -> None:
        p = temp_reports / "functional_runtime_mvp_replay_report.json"
        if p.exists():
            p.write_text("{{{corrupted json!!!", encoding="utf-8")
        rc = _run_validator("validate_functional_runtime_mvp_replay", temp_reports)
        assert rc != 0, "Validator should reject corrupt JSON"

    def test_validator_rejects_stale_report_commit(self, temp_reports: Path) -> None:
        p = temp_reports / "functional_runtime_mvp_proof_bundle.json"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            data["git_commit"] = "aaaaaaa"
            p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        rc = _run_validator("validate_functional_runtime_mvp_anti_false_pass", temp_reports)
        assert rc != 0, "Validator should reject stale git commit"

    def test_anti_false_pass_audit_rejects_all_attacks(self, temp_reports: Path) -> None:
        # Delete the audit — validator must fail
        p = temp_reports / "functional_runtime_mvp_anti_false_pass_audit.json"
        if p.exists():
            p.unlink()
        rc = _run_validator("validate_functional_runtime_mvp_reports", temp_reports)
        assert rc != 0, "Validator should reject missing anti-false-PASS audit"
