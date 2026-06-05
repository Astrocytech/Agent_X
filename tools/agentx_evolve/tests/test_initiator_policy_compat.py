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


class TestCompatPolicyRegistry:
    def test_policy_registry_loaded(self):
        assert PolicyRegistry is not None

    def test_get_policy_registry(self, tmp_path):
        reg = get_policy_registry(repo_root=tmp_path)
        assert reg is not None


class TestInitiatorPolicyCompat:
    def test_default_init(self):
        compat = InitiatorPolicyCompat()
        assert compat.get_repo_root() is not None
        assert compat.get_policy_runtime_root().name == "policies"

    def test_custom_repo_root(self, tmp_path):
        compat = InitiatorPolicyCompat(repo_root=tmp_path)
        assert compat.get_repo_root() == tmp_path
        assert compat.get_policy_runtime_root() == tmp_path / ".agentx-init" / "policies"

    def test_validate_schema(self):
        compat = InitiatorPolicyCompat()
        result = compat.validate_schema({"schema_id": "capability_policy.schema.json"}, "capability_policy.schema.json")
        assert isinstance(result, dict)

    def test_write_json_atomic(self, tmp_path):
        compat = InitiatorPolicyCompat(repo_root=tmp_path)
        path = tmp_path / "test.json"
        result = compat.write_json_atomic(path, {"key": "value"})
        assert isinstance(result, dict)
        assert result.get("success") is True
        import json
        data = json.loads(path.read_text())
        assert data["key"] == "value"

    def test_append_audit_event(self, tmp_path):
        compat = InitiatorPolicyCompat(repo_root=tmp_path)
        result = compat.append_audit_event({"event": "test"})
        assert isinstance(result, dict)
        log = compat.get_policy_runtime_root() / "policy_decisions.jsonl"
        assert log.exists()

    def test_append_policy_decision(self, tmp_path):
        compat = InitiatorPolicyCompat(repo_root=tmp_path)
        d = PolicyDecision(decision_id="pd-1", decision=DECISION_ALLOW)
        result = compat.append_policy_decision(d)
        assert isinstance(result, dict)

    def test_write_latest_policy_decision(self, tmp_path):
        compat = InitiatorPolicyCompat(repo_root=tmp_path)
        d = PolicyDecision(decision_id="pd-1", decision=DECISION_ALLOW)
        result = compat.write_latest_policy_decision(d)
        assert isinstance(result, dict)
        latest = compat.get_policy_runtime_root() / "latest_policy_decision.json"
        assert latest.exists()
