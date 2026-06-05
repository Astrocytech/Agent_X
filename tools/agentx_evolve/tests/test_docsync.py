import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest

from agentx_evolve.docsync.doc_sync import (
    DocDrift, DocSyncResult, DocSyncChecker, SchemaDocChecker,
    DocSyncReport,
    DS_SCHEMA_VERSION, DS_SCHEMA_ID,
    DS_PASS, DS_FAIL, DS_WARN, DS_SKIP,
    canonical_json, sha256_dict, write_json_atomic, append_jsonl,
    docsync_runs_dir,
)


class TestDocDriftCreation:
    def test_docdrift_creation(self):
        drift = DocDrift(location="README.md", expected="foo", actual="bar", severity="error")
        assert drift.location == "README.md"
        assert drift.expected == "foo"
        assert drift.actual == "bar"
        assert drift.severity == "error"


class TestDocSyncChecker:
    def test_docsync_checker_pass(self):
        checker = DocSyncChecker()
        checks = [
            {"location": "README.md", "expected": "foo", "actual": "foo"},
        ]
        result = checker.check(checks)
        assert result.passed is True
        assert result.total_checks == 1
        assert len(result.drifts) == 0

    def test_docsync_checker_drift(self):
        checker = DocSyncChecker()
        checks = [
            {"location": "README.md", "expected": "foo", "actual": "bar"},
        ]
        result = checker.check(checks)
        assert result.passed is False
        assert len(result.drifts) == 1
        assert result.drifts[0].location == "README.md"
        assert result.drifts[0].expected == "foo"
        assert result.drifts[0].actual == "bar"


class TestSchemaDocChecker:
    def test_schema_doc_checker_mismatch(self):
        checker = SchemaDocChecker()
        schema_fields = [{"name": "field_a"}, {"name": "field_b"}]
        doc_fields = ["field_a"]
        mismatches = checker.check(schema_fields, doc_fields)
        assert any("field_b" in m for m in mismatches)

    def test_schema_doc_checker_match(self):
        checker = SchemaDocChecker()
        schema_fields = [{"name": "field_a"}, {"name": "field_b"}]
        doc_fields = ["field_a", "field_b"]
        mismatches = checker.check(schema_fields, doc_fields)
        assert len(mismatches) == 0


class TestDocSyncPersistence:
    def test_run_check_writes_report(self, tmp_path: Path):
        checker = DocSyncChecker()
        checks = [
            {"location": "doc.md", "expected": "hello", "actual": "hello"},
            {"location": "doc.md", "expected": "world", "actual": "nope"},
        ]
        report = checker.run_check(checks, tmp_path)
        report_path = docsync_runs_dir(tmp_path) / "doc_sync_check_report.json"
        assert report_path.exists()
        data = json.loads(report_path.read_text())
        assert data["check_id"] == report.check_id
        assert data["total_checks"] == 2
        assert data["passed"] is False
        assert len(data["drifts"]) == 1

    def test_append_check_history(self, tmp_path: Path):
        checker = DocSyncChecker()
        checks = [{"location": "x.md", "expected": "a", "actual": "a"}]
        report = checker.run_check(checks, tmp_path)
        history_path = docsync_runs_dir(tmp_path) / "doc_sync_history.jsonl"
        assert history_path.exists()
        lines = history_path.read_text().strip().split("\n")
        assert len(lines) >= 1
        last = json.loads(lines[-1])
        assert last["check_id"] == report.check_id

    def test_docsync_lock_acquire_release(self, tmp_path: Path):
        checker = DocSyncChecker()
        lock = checker.acquire_docsync_lock(tmp_path)
        assert lock["acquired"] is True
        checker.release_docsync_lock(lock, tmp_path)
        lock_path = docsync_runs_dir(tmp_path) / ".docsync.lock"
        assert not lock_path.exists()
