import pytest
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
