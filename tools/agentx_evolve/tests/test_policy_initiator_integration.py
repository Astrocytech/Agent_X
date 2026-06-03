import pytest
from agentx_evolve.policy.policy_models import (
    DECISION_ALLOW,
    PolicyDecision,
)
from agentx_evolve.policy.initiator_policy_compat import (
    InitiatorPolicyCompat,
    get_policy_registry,
)
from agentx_evolve.policy.policy_registry import PolicyRegistry


def test_policy_registry_loaded():
    assert PolicyRegistry is not None


def test_get_policy_registry(tmp_path):
    reg = get_policy_registry(repo_root=tmp_path)
    assert reg is not None


def test_compat_default_init():
    compat = InitiatorPolicyCompat()
    assert compat.get_repo_root() is not None
    assert compat.get_policy_runtime_root().name == "policies"


def test_compat_custom_repo_root(tmp_path):
    compat = InitiatorPolicyCompat(repo_root=tmp_path)
    assert compat.get_repo_root() == tmp_path
    assert compat.get_policy_runtime_root() == tmp_path / ".agentx-init" / "policies"


def test_compat_validate_schema():
    compat = InitiatorPolicyCompat()
    result = compat.validate_schema(
        {"schema_id": "capability_policy.schema.json"},
        "capability_policy.schema.json",
    )
    assert isinstance(result, dict)


def test_compat_write_json_atomic(tmp_path):
    compat = InitiatorPolicyCompat(repo_root=tmp_path)
    path = tmp_path / "test.json"
    result = compat.write_json_atomic(path, {"key": "value"})
    assert isinstance(result, dict)
    assert result.get("success") is True
    import json
    data = json.loads(path.read_text())
    assert data["key"] == "value"


def test_compat_append_audit_event(tmp_path):
    compat = InitiatorPolicyCompat(repo_root=tmp_path)
    result = compat.append_audit_event({"event": "test"})
    assert isinstance(result, dict)
    log = compat.get_policy_runtime_root() / "policy_decisions.jsonl"
    assert log.exists()


def test_compat_append_policy_decision(tmp_path):
    compat = InitiatorPolicyCompat(repo_root=tmp_path)
    d = PolicyDecision(decision_id="pd-1", decision=DECISION_ALLOW)
    result = compat.append_policy_decision(d)
    assert isinstance(result, dict)


def test_compat_write_latest_policy_decision(tmp_path):
    compat = InitiatorPolicyCompat(repo_root=tmp_path)
    d = PolicyDecision(decision_id="pd-1", decision=DECISION_ALLOW)
    result = compat.write_latest_policy_decision(d)
    assert isinstance(result, dict)
    latest = compat.get_policy_runtime_root() / "latest_policy_decision.json"
    assert latest.exists()


def test_compat_append_policy_decision_fallback(tmp_path):
    compat = InitiatorPolicyCompat(repo_root=tmp_path)
    d = PolicyDecision(decision_id="pd-2", decision=DECISION_ALLOW)
    result = compat.append_policy_decision(d)
    assert isinstance(result, dict)
    assert result.get("success") is True


def test_compat_latest_policy_decision_content(tmp_path):
    compat = InitiatorPolicyCompat(repo_root=tmp_path)
    d = PolicyDecision(decision_id="pd-3", decision=DECISION_ALLOW)
    compat.write_latest_policy_decision(d)
    import json
    latest = compat.get_policy_runtime_root() / "latest_policy_decision.json"
    data = json.loads(latest.read_text())
    assert data.get("decision_id") == "pd-3"
    assert data.get("decision") == DECISION_ALLOW
