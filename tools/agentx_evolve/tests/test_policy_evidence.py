import pytest
from agentx_evolve.policy.policy_evidence import (
    append_policy_decision,
    append_policy_violation,
    build_policy_audit_event,
    write_latest_policy_decision,
    write_policy_decision,
)
from agentx_evolve.policy.policy_models import (
    DECISION_ALLOW,
    EFFECT_READ,
    ROLE_ORCHESTRATOR,
    PolicyDecision,
)


@pytest.fixture
def sample_decision():
    return PolicyDecision(
        decision_id="pd-1",
        caller_role=ROLE_ORCHESTRATOR,
        tool_name="read",
        requested_effect=EFFECT_READ,
        decision=DECISION_ALLOW,
        reason="ALLOW_BY_CAPABILITY",
    )


class TestAppendPolicyDecision:
    def test_appends_line(self, tmp_path, sample_decision):
        result = append_policy_decision(sample_decision, tmp_path)
        assert isinstance(result, dict)
        assert result.get("success") is True

    def test_appends_multiple(self, tmp_path, sample_decision):
        r1 = append_policy_decision(sample_decision, tmp_path)
        r2 = append_policy_decision(sample_decision, tmp_path)
        assert isinstance(r1, dict)
        assert isinstance(r2, dict)
        assert r1.get("success") is True
        assert r2.get("success") is True


from agentx_evolve.policy.policy_models import PolicyViolation


class TestAppendPolicyViolation:
    def test_appends_violation(self, tmp_path):
        violation = PolicyViolation(violation_id="v-1", reason="UNAUTHORIZED")
        result = append_policy_violation(violation, tmp_path)
        assert isinstance(result, dict)
        assert result.get("success") is True


class TestWriteLatestPolicyDecision:
    def test_writes_json(self, tmp_path, sample_decision):
        result = write_latest_policy_decision(sample_decision, tmp_path)
        assert isinstance(result, dict)
        assert result.get("success") is True

    def test_overwrites(self, tmp_path, sample_decision):
        write_latest_policy_decision(sample_decision, tmp_path)
        d2 = PolicyDecision(decision_id="pd-2", decision=DECISION_ALLOW)
        result = write_latest_policy_decision(d2, tmp_path)
        assert isinstance(result, dict)
        assert result.get("success") is True


class TestWritePolicyDecision:
    def test_writes(self, tmp_path, sample_decision):
        result = write_policy_decision(sample_decision, tmp_path)
        assert isinstance(result, dict)
        assert result.get("success") is True


class TestBuildPolicyAuditEvent:
    def test_creates_from_decision(self, sample_decision):
        audit = build_policy_audit_event(sample_decision, success=True)
        assert audit.audit_id != ""
        assert audit.decision_id == "pd-1"
        assert audit.caller_role == ROLE_ORCHESTRATOR
        assert audit.success is True
        assert audit.event_type == "policy_evaluation"

    def test_failure(self, sample_decision):
        audit = build_policy_audit_event(sample_decision, success=False)
        assert audit.success is False
