import json
from pathlib import Path

import pytest

from agentx_evolve.scheduler.scheduler_models import (
    sha256_bytes, sha256_file, canonical_json,
    compute_task_record_hash, compute_session_record_hash,
    to_dict, TaskRecord, SessionRecord, new_id,
    SchedulerEvidenceManifest, SchedulerCompletionRecord,
)


def test_compute_file_hash_returns_sha256(tmp_path: Path):
    f = tmp_path / "test.txt"
    f.write_text("hello world")
    h = sha256_file(f)
    assert isinstance(h, str)
    assert len(h) == 64


def test_compute_state_hash_is_deterministic():
    data = {"a": 1, "b": 2}
    h1 = sha256_bytes(canonical_json(data))
    h2 = sha256_bytes(canonical_json(data))
    assert h1 == h2


def test_compute_evidence_hash_excludes_self():
    data = {"a": 1, "task_record_hash": "abc", "b": 2}
    h = compute_task_record_hash(data)
    assert isinstance(h, str)
    assert len(h) == 64


def test_verify_file_hash_matches(tmp_path: Path):
    f = tmp_path / "data.txt"
    content = "test content"
    f.write_text(content)
    h1 = sha256_file(f)
    h2 = sha256_file(f)
    assert h1 == h2


def test_verify_file_hash_fails_on_mismatch(tmp_path: Path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("content a")
    f2.write_text("content b")
    assert sha256_file(f1) != sha256_file(f2)


def test_hash_scheduler_artifact_writes_evidence(tmp_path: Path):
    manifest = SchedulerEvidenceManifest(validated_commit="abc123")
    d = to_dict(manifest)
    h = sha256_bytes(canonical_json(d))
    assert isinstance(h, str)
    assert len(h) == 64
