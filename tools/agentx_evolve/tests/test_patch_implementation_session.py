import json
from pathlib import Path
from agentx_evolve.patch_execution._v1.patch_models import (
    PatchSession, PatchAction, ImplementationEvidence,
    MutationAllowlist, ApprovedMutation,
    SESSION_CREATED, SESSION_LOADED, SESSION_ACCEPTED, SESSION_FAILED,
)
from agentx_evolve.security.security_models import (
    SandboxPolicy, DECISION_ALLOW, DECISION_BLOCK,
)
from agentx_evolve.patch_execution._v1.implementation_session import ImplementationSession


def _make_default_policy() -> SandboxPolicy:
    return SandboxPolicy(
        policy_id="test-policy",
        repo_root="/tmp",
        protected_paths=["L0/"],
        allowlisted_write_paths=[".agentx-init/"],
    )


class TestImplementationSessionConstruction:
    def test_default_construction(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy)
        assert session.session_id != ""
        assert session.session.status.current == SESSION_CREATED

    def test_with_custom_session_id(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy, session_id="my-session")
        assert session.session_id == "my-session"

    def test_with_mutation_allowlist(self, tmp_path):
        policy = _make_default_policy()
        allowlist = MutationAllowlist(
            allowlist_id="mal-1",
            mutations=[ApprovedMutation(target_path="src/", allowed_change_types=["UPDATE"])],
        )
        session = ImplementationSession(tmp_path, policy, mutation_allowlist=allowlist)
        assert session._mutation_allowlist is not None


class TestImplementationSessionLoadProposal:
    def test_load_proposal_with_actions(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy)
        proposal = {
            "actions": [
                {"target_file": "src/main.py", "change_type": "UPDATE",
                 "old_text": "old", "new_text": "new"},
                {"target_file": "src/utils.py", "change_type": "CREATE",
                 "new_text": "content"},
            ],
        }
        result = session.load_proposal(proposal)
        assert result.status.current == "PROPOSAL_LOADED"
        assert len(result.actions) == 2
        assert "src/main.py" in result.target_paths
        assert "src/utils.py" in result.target_paths

    def test_load_proposal_with_proposed_changes(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy)
        proposal = {
            "proposed_changes": [
                {"file": "test.py", "type": "UPDATE", "old_text": "a", "new_text": "b"},
            ],
        }
        session.load_proposal(proposal)
        assert len(session.session.actions) == 1
        assert session.session.actions[0].target_file == "test.py"


class TestImplementationSessionGovernance:
    def test_check_governance_missing_id(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy, governance_decision_id="")
        session._session.status.transition_to(SESSION_LOADED)
        session._session.status.transition_to("PROPOSAL_LOADED")
        result = session.check_governance()
        assert result.decision == DECISION_BLOCK
        assert "Governance decision ID is required" in result.reason

    def test_check_governance_with_id(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy, governance_decision_id="gv-1")
        session._session.status.transition_to(SESSION_LOADED)
        session._session.status.transition_to("PROPOSAL_LOADED")
        result = session.check_governance()
        assert result.decision == DECISION_ALLOW


class TestImplementationSessionLifecycle:
    def test_session_property(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy, session_id="lifecycle-test")
        assert session.session_id == "lifecycle-test"
        assert session.session.status.current == SESSION_CREATED

    def test_accept(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy, session_id="accept-test")
        session._session.status.transition_to(SESSION_LOADED)
        session._session.status.transition_to("PROPOSAL_LOADED")
        session._session.status.transition_to("GOVERNANCE_CHECKED")
        session._session.status.transition_to("PATCH_APPLIED")
        session._session.status.transition_to("VALIDATED")
        result = session.accept()
        assert result.status.current == SESSION_ACCEPTED

    def test_fail(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy, session_id="fail-test")
        result = session.fail(reason="Something went wrong")
        assert result.status.current == SESSION_FAILED
        assert "Something went wrong" in result.errors

    def test_rollback(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy, session_id="rollback-test")
        session._session.status.transition_to(SESSION_LOADED)
        session._session.status.transition_to("PROPOSAL_LOADED")
        session._session.status.transition_to("GOVERNANCE_CHECKED")
        session._session.status.transition_to("PATCH_APPLIED")
        result = session.rollback()
        assert result.status.current == "ROLLED_BACK"

    def test_validate_without_commands(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy, session_id="validate-test")
        session._session.status.transition_to(SESSION_LOADED)
        session._session.status.transition_to("PROPOSAL_LOADED")
        session._session.status.transition_to("GOVERNANCE_CHECKED")
        session._session.status.transition_to("PATCH_APPLIED")
        result = session.validate()
        assert result.validation_result is not None


class TestResolveAllowlistFromGovernance:
    def test_no_governance_id_returns_empty(self, tmp_path):
        policy = _make_default_policy()
        session = ImplementationSession(tmp_path, policy, governance_decision_id="missing-gv")
        allowlist = session._resolve_allowlist_from_governance()
        assert allowlist.is_empty()

    def test_with_governance_file(self, tmp_path):
        policy = _make_default_policy()
        gv_path = tmp_path / ".agentx-init" / "governance" / "decisions" / "gv-123.json"
        gv_path.parent.mkdir(parents=True)
        gv_path.write_text(json.dumps({
            "mutation_allowlist": [
                {"target_path": "src/", "allowed_change_types": ["UPDATE"]},
            ],
        }))
        session = ImplementationSession(tmp_path, policy, governance_decision_id="gv-123")
        allowlist = session._resolve_allowlist_from_governance()
        assert allowlist.is_empty() is False
        assert allowlist.allows_mutation("src/main.py", "UPDATE") is True

    def test_corrupt_governance_file(self, tmp_path):
        policy = _make_default_policy()
        gv_path = tmp_path / ".agentx-init" / "governance" / "decisions" / "gv-bad.json"
        gv_path.parent.mkdir(parents=True)
        gv_path.write_text("not json")
        session = ImplementationSession(tmp_path, policy, governance_decision_id="gv-bad")
        allowlist = session._resolve_allowlist_from_governance()
        assert allowlist.is_empty()
        assert len(allowlist.errors) > 0
