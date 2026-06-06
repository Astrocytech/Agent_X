from agentx_evolve.git.git_mutation_gate import MutationGate
from agentx_evolve.git.git_models import (
    GitMutationRequest, GS_SUCCESS, GS_BLOCKED,
)


class TestMutationGate:
    def setup_method(self):
        self.gate = MutationGate()

    def test_passes_with_all_authorities(self):
        req = GitMutationRequest(
            request_id="mr-001",
            operation="STAGE",
            repo_path="/tmp",
            policy_decision_id="pd-001",
            sandbox_decision_id="sd-001",
            promotion_gate_id="pg-001",
        )
        result = self.gate.check(req)
        assert result.status == GS_SUCCESS
        assert result.message == "All gates passed"

    def test_blocks_missing_policy_decision(self):
        req = GitMutationRequest(
            request_id="mr-002",
            operation="COMMIT",
            repo_path="/tmp",
            sandbox_decision_id="sd-001",
            promotion_gate_id="pg-001",
        )
        result = self.gate.check(req)
        assert result.status == GS_BLOCKED
        assert "policy_decision_id" in result.message
        assert "Missing required authorities" in result.message

    def test_blocks_missing_sandbox_decision(self):
        req = GitMutationRequest(
            request_id="mr-003",
            operation="STAGE",
            repo_path="/tmp",
            policy_decision_id="pd-001",
            promotion_gate_id="pg-001",
        )
        result = self.gate.check(req)
        assert result.status == GS_BLOCKED
        assert "sandbox_decision_id" in result.message

    def test_blocks_missing_promotion_gate(self):
        req = GitMutationRequest(
            request_id="mr-004",
            operation="PUSH",
            repo_path="/tmp",
            policy_decision_id="pd-001",
            sandbox_decision_id="sd-001",
        )
        result = self.gate.check(req)
        assert result.status == GS_BLOCKED
        assert "promotion_gate_id" in result.message

    def test_blocks_missing_all_authorities(self):
        req = GitMutationRequest(
            request_id="mr-005",
            operation="STAGE",
            repo_path="/tmp",
        )
        result = self.gate.check(req)
        assert result.status == GS_BLOCKED
        assert "policy_decision_id" in result.message
        assert "sandbox_decision_id" in result.message
        assert "promotion_gate_id" in result.message

    def test_success_returns_authority_refs(self):
        req = GitMutationRequest(
            request_id="mr-006",
            operation="COMMIT",
            repo_path="/tmp",
            policy_decision_id="pd-001",
            sandbox_decision_id="sd-001",
            promotion_gate_id="pg-001",
        )
        result = self.gate.check(req)
        assert result.authority_refs["policy_decision_id"] == "pd-001"
        assert result.authority_refs["sandbox_decision_id"] == "sd-001"
        assert result.authority_refs["promotion_gate_id"] == "pg-001"

    def test_result_has_timestamp(self):
        req = GitMutationRequest(
            request_id="mr-007",
            operation="STAGE",
            repo_path="/tmp",
            policy_decision_id="pd-001",
            sandbox_decision_id="sd-001",
            promotion_gate_id="pg-001",
        )
        result = self.gate.check(req)
        assert "T" in result.timestamp
