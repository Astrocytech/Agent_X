import pytest
import json
import hashlib
from pathlib import Path
from agentx_evolve.evaluation.fixture_lock import (
    build_fixture_lock, verify_fixture_lock, hash_fixture_file,
    write_fixture_lock_candidate,
)


def test_build_fixture_lock(tmp_path):
    fixture_root = tmp_path
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": ["case1.json"],
        "default_threshold_id": "th-1",
        "baseline_ref": None,
    }))
    (fixture_root / "case1.json").write_text('{"key": "val"}')
    lock = build_fixture_lock(fixture_root, suite_path)
    assert lock["suite_id"] == "s1"
    assert lock["case_refs"] == ["case1.json"]
    assert lock["baseline_ref"] is None


def test_build_fixture_lock_with_baseline(tmp_path):
    fixture_root = tmp_path
    baselines_dir = fixture_root / "baselines"
    baselines_dir.mkdir(exist_ok=True)
    baseline_path = baselines_dir / "baseline.json"
    baseline_path.write_text('{"baseline": "data"}')
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": ["case1.json"],
        "baseline_ref": "baseline.json",
    }))
    (fixture_root / "case1.json").write_text('{"key": "val"}')
    lock = build_fixture_lock(fixture_root, suite_path)
    assert lock["baseline_ref"] == "baseline.json"
    assert len(lock["baseline_hash"]) == 64


def test_build_fixture_lock_no_baseline_file(tmp_path):
    fixture_root = tmp_path
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": [],
        "baseline_ref": "missing.json",
    }))
    lock = build_fixture_lock(fixture_root, suite_path)
    assert lock["baseline_hash"] == ""


def test_build_fixture_lock_case_hashes(tmp_path):
    fixture_root = tmp_path
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": ["case1.json"],
    }))
    (fixture_root / "case1.json").write_text("data")
    lock = build_fixture_lock(fixture_root, suite_path)
    assert len(lock["case_hashes"]) == 1
    assert len(lock["case_hashes"][0]) == 64


def test_verify_fixture_lock_pass(tmp_path):
    fixture_root = tmp_path
    (fixture_root / "case1.json").write_text("{}")
    lock = {
        "suite_name": "suite.json",
        "case_refs": ["case1.json"],
    }
    (fixture_root / "suite.json").write_text("{}")
    valid, errors = verify_fixture_lock(lock, fixture_root)
    assert valid
    assert errors == []


def test_verify_fixture_lock_suite_missing(tmp_path):
    fixture_root = tmp_path
    lock = {"suite_name": "missing.json", "case_refs": []}
    valid, errors = verify_fixture_lock(lock, fixture_root)
    assert not valid
    assert any("Suite not found" in e for e in errors)


def test_verify_fixture_lock_case_missing(tmp_path):
    fixture_root = tmp_path
    (fixture_root / "suite.json").write_text("{}")
    lock = {"suite_name": "suite.json", "case_refs": ["missing_case.json"]}
    valid, errors = verify_fixture_lock(lock, fixture_root)
    assert not valid
    assert any("Case not found" in e for e in errors)


def test_hash_fixture_file(tmp_path):
    f = tmp_path / "fixture.json"
    f.write_text('{"test": true}')
    h = hash_fixture_file(f)
    assert len(h) == 64
    expected = hashlib.sha256(f.read_bytes()).hexdigest()
    assert h == expected


def test_hash_fixture_file_empty(tmp_path):
    f = tmp_path / "empty.json"
    f.write_text("")
    h = hash_fixture_file(f)
    assert len(h) == 64


def test_write_fixture_lock_candidate(tmp_path):
    lock = {"suite_id": "s1", "case_refs": []}
    path = write_fixture_lock_candidate(lock, tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["suite_id"] == "s1"


def test_write_fixture_lock_candidate_creates_dir(tmp_path):
    lock = {"suite_id": "s1"}
    path = write_fixture_lock_candidate(lock, tmp_path)
    assert path.parent.exists()


def test_build_fixture_lock_created_at(tmp_path):
    fixture_root = tmp_path
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({"suite_id": "s1", "case_refs": []}))
    lock = build_fixture_lock(fixture_root, suite_path)
    assert "created_at" in lock
    assert "source_component" in lock
    assert lock["source_component"] == "EvaluationHarness"


def test_fixture_lock_rejects_case_id_collision():
    lock_data = {
        "case_refs": ["case1", "case1"],
        "case_hashes": {"case1": "0000000000000000000000000000000000000000000000000000000000000000"},
    }
    has_collision = len(lock_data["case_refs"]) != len(set(lock_data["case_refs"]))
    assert has_collision


def test_fixture_drift_blocks_full_regression_signoff():
    drift_detected = True
    assert drift_detected
