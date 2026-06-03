import json
import pytest
import threading
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from agentx_evolve.security.security_models import SandboxDecision, SandboxViolation
from agentx_evolve.security.sandbox_evidence import (
    append_sandbox_decision,
    append_sandbox_violation,
    write_latest_sandbox_decision,
)
from agentx_evolve.security.initiator_compat import InitiatorCompat


def _invalid_decision() -> SandboxDecision:
    return SandboxDecision(
        decision_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        operation="READ",
        target=None,
        decision="INVALID_DECISION_VALUE",
        reason="",
    )


def _invalid_violation() -> SandboxViolation:
    return SandboxViolation(
        violation_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        operation="WRITE",
        target=None,
        violation_type="",
        severity="",
        reason="",
    )


@pytest.fixture
def repo_root(tmp_path):
    return tmp_path / "repo"


@pytest.fixture
def compat():
    return InitiatorCompat()


def test_append_sandbox_decision_without_compat_succeeds(repo_root):
    decision = _invalid_decision()
    result = append_sandbox_decision(decision, repo_root, compat=None)
    assert result["status"] == "APPENDED"
    assert Path(result["path"]).exists()


def test_append_sandbox_decision_blocks_invalid_schema(repo_root, compat):
    decision = _invalid_decision()
    result = append_sandbox_decision(decision, repo_root, compat=compat)
    assert result["status"] == "FAILED"
    assert result["error"] == "SCHEMA_VALIDATION_FAILED"
    assert result["schema_id"] == "sandbox_decision.schema.json"


def test_append_sandbox_violation_blocks_invalid_schema(repo_root, compat):
    violation = _invalid_violation()
    result = append_sandbox_violation(violation, repo_root, compat=compat)
    assert result["status"] == "FAILED"
    assert result["error"] == "SCHEMA_VALIDATION_FAILED"
    assert result["schema_id"] == "sandbox_violation.schema.json"


def test_write_latest_sandbox_decision_blocks_invalid_schema(repo_root, compat):
    decision = _invalid_decision()
    result = write_latest_sandbox_decision(decision, repo_root, compat=compat)
    assert result["status"] == "FAILED"
    assert result["error"] == "SCHEMA_VALIDATION_FAILED"


def test_append_only_preserves_previous_entries(repo_root):
    d1 = SandboxDecision(
        decision_id="id1", timestamp="2025-01-01T00:00:00",
        operation="READ", target="a.txt", decision="ALLOW", reason="ok",
    )
    d2 = SandboxDecision(
        decision_id="id2", timestamp="2025-01-01T00:00:01",
        operation="READ", target="b.txt", decision="ALLOW", reason="ok",
    )
    r1 = append_sandbox_decision(d1, repo_root, compat=None)
    assert r1["status"] == "APPENDED"
    r2 = append_sandbox_decision(d2, repo_root, compat=None)
    assert r2["status"] == "APPENDED"
    lines = Path(r1["path"]).read_text().strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["decision_id"] == "id1"
    assert json.loads(lines[1])["decision_id"] == "id2"


def test_concurrent_appends_with_locking(repo_root):
    results: list[dict] = []
    errors: list[Exception] = []

    def append_d(dec_id: str):
        try:
            d = SandboxDecision(
                decision_id=dec_id, timestamp="2025-01-01T00:00:00",
                operation="READ", target=f"{dec_id}.txt",
                decision="ALLOW", reason="concurrent",
            )
            r = append_sandbox_decision(d, repo_root, compat=None)
            results.append(r)
        except Exception as e:
            errors.append(e)

    threads = [
        threading.Thread(target=append_d, args=(f"concurrent-{i}",))
        for i in range(10)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent appends failed: {errors}"
    assert len(results) == 10
    path = results[0]["path"]
    lines = Path(path).read_text().strip().splitlines()
    assert len(lines) == 10, f"Expected 10 lines, got {len(lines)}"


def test_degraded_mode_fallback_still_appends(repo_root):
    decision = SandboxDecision(
        decision_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        operation="WRITE",
        target="/etc/passwd",
        decision="BLOCK",
        reason="test",
    )
    result = append_sandbox_decision(decision, repo_root, compat=None)
    assert result["status"] == "APPENDED"
    assert Path(result["path"]).exists()
