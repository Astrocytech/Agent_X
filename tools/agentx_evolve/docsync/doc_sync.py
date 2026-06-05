from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import json
import os
import time
from typing import Any
from agentx_evolve.model.model_models import new_id, utc_now_iso, to_dict

DS_SCHEMA_VERSION = "1.0"
DS_SCHEMA_ID = "doc_sync_check.schema.json"

DS_PASS = "PASS"
DS_FAIL = "FAIL"
DS_WARN = "WARN"
DS_SKIP = "SKIP"

_LOCK_TIMEOUT_SECONDS = 10


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_dict(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def write_json_atomic(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(canonical_json(data) + "\n")
    tmp.replace(path)
    return path


def append_jsonl(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(canonical_json(data) + "\n")
    return path


def docsync_runs_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "docsync"


@dataclass
class DocDrift:
    location: str = ""
    expected: str = ""
    actual: str = ""
    severity: str = "info"

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class DocSyncResult:
    total_checks: int = 0
    drifts: list[DocDrift] = field(default_factory=list)
    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class DocSyncReport:
    schema_version: str = DS_SCHEMA_VERSION
    schema_id: str = DS_SCHEMA_ID
    check_id: str = ""
    created_at: str = ""
    total_checks: int = 0
    drifts: list[DocDrift] = field(default_factory=list)
    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    checks: list[dict] = field(default_factory=list)
    result_hash: str = ""

    def to_dict(self) -> dict:
        return to_dict(self)


class DocSyncChecker:
    def check(self, checks: list[dict]) -> DocSyncResult:
        result = DocSyncResult()
        for c in checks:
            result.total_checks += 1
            expected = c.get("expected", "")
            actual = c.get("actual", "")
            location = c.get("location", "unknown")
            if expected != actual:
                drift = DocDrift(
                    location=location,
                    expected=expected,
                    actual=actual,
                    severity=c.get("severity", "warn"),
                )
                result.drifts.append(drift)
                result.passed = False
        return result

    def run_check(self, checks: list[dict], repo_root: Path) -> DocSyncReport:
        lock = self.acquire_docsync_lock(repo_root)
        try:
            result = self.check(checks)
            report = DocSyncReport(
                check_id=new_id("ds-check-"),
                created_at=utc_now_iso(),
                total_checks=result.total_checks,
                drifts=result.drifts,
                passed=result.passed,
                warnings=list(result.warnings),
                errors=list(result.errors),
                checks=checks,
            )
            payload = {k: v for k, v in to_dict(report).items() if k != "result_hash"}
            report.result_hash = sha256_dict(payload)
            self.write_check_report(report, repo_root)
            self.append_check_history(report, repo_root)
            return report
        finally:
            self.release_docsync_lock(lock, repo_root)

    def write_check_report(self, report: DocSyncReport, repo_root: Path) -> Path:
        dest = docsync_runs_dir(repo_root) / "doc_sync_check_report.json"
        return write_json_atomic(dest, to_dict(report))

    def append_check_history(self, report: DocSyncReport, repo_root: Path) -> Path:
        dest = docsync_runs_dir(repo_root) / "doc_sync_history.jsonl"
        return append_jsonl(dest, to_dict(report))

    def acquire_docsync_lock(self, repo_root: Path, timeout_seconds: int = _LOCK_TIMEOUT_SECONDS) -> object:
        lock_path = docsync_runs_dir(repo_root) / ".docsync.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return {"acquired": True, "path": str(lock_path)}
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Could not acquire docsync lock within {timeout_seconds}s: {lock_path}")
                time.sleep(0.1)

    def release_docsync_lock(self, lock: object, repo_root: Path) -> None:
        lock_path = docsync_runs_dir(repo_root) / ".docsync.lock"
        try:
            lock_path.unlink(missing_ok=True)
        except FileNotFoundError:
            pass


class SchemaDocChecker:
    def check(self, schema_fields: list[dict], doc_fields: list[str]) -> list[str]:
        mismatches = []
        for field in schema_fields:
            name = field.get("name", "")
            if name and name not in doc_fields:
                mismatches.append(f"Schema field '{name}' missing from docs")
        for doc in doc_fields:
            if not any(f.get("name") == doc for f in schema_fields):
                mismatches.append(f"Doc field '{doc}' missing from schema")
        return mismatches

    def check_with_schema(self, schema_path: Path, doc_fields: list[str]) -> list[str]:
        schema_data = json.loads(schema_path.read_text())
        schema_fields = []
        props = schema_data.get("properties", {})
        for prop_name in props:
            schema_fields.append({"name": prop_name})
        return self.check(schema_fields, doc_fields)
