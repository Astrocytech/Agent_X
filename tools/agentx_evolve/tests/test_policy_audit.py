import pytest
from agentx_evolve.policy.policy_models import (
    PolicyAuditEntry, PAE_ALLOW, PAE_BLOCK, log_policy_decision,
    get_policy_audit_log, clear_policy_audit_log, get_policy_audit_by_session,
)


@pytest.fixture(autouse=True)
def _clear_audit():
    clear_policy_audit_log()
    yield
    clear_policy_audit_log()


class TestPolicyAudit:
    def test_audit_entry_records_decision(self):
        entry = log_policy_decision(
            session_id="sess-001",
            decision=PAE_ALLOW,
            reason="allowed by capability",
        )
        assert entry.session_id == "sess-001"
        assert entry.decision == PAE_ALLOW
        assert entry.reason == "allowed by capability"
        assert entry.entry_id.startswith("pae-")

    def test_audit_log_retrieves_by_session(self):
        log_policy_decision(session_id="sess-a", decision=PAE_ALLOW)
        log_policy_decision(session_id="sess-b", decision=PAE_BLOCK)
        log_policy_decision(session_id="sess-a", decision=PAE_BLOCK)
        results = get_policy_audit_by_session("sess-a")
        assert len(results) == 2
        results_b = get_policy_audit_by_session("sess-b")
        assert len(results_b) == 1

    def test_audit_log_returns_all(self):
        log_policy_decision(session_id="sess-001", decision=PAE_ALLOW)
        log_policy_decision(session_id="sess-002", decision=PAE_BLOCK)
        all_entries = get_policy_audit_log()
        assert len(all_entries) == 2

    def test_block_decision(self):
        entry = log_policy_decision(
            session_id="sess-001",
            decision=PAE_BLOCK,
            reason="policy denied",
            metadata={"tool": "bash", "effect": "EXECUTE"},
        )
        assert entry.decision == PAE_BLOCK
        assert entry.metadata["tool"] == "bash"

    def test_clear_audit_log(self):
        log_policy_decision(session_id="sess-001", decision=PAE_ALLOW)
        assert len(get_policy_audit_log()) == 1
        clear_policy_audit_log()
        assert get_policy_audit_log() == []

    def test_policy_audit_entry_serializes(self):
        entry = PolicyAuditEntry(
            entry_id="pae-001",
            session_id="sess-001",
            decision=PAE_BLOCK,
            reason="test",
        )
        d = entry.to_dict()
        assert d["entry_id"] == "pae-001"
        assert d["decision"] == "BLOCK"
