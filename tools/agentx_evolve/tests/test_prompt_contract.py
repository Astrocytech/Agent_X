from __future__ import annotations

import pytest
from agentx_evolve.contracts.prompt_contract import PromptContract
from agentx_evolve.contracts.prompt_contract_registry import PromptContractRegistry


SAMPLE_CONTRACT = PromptContract(
    contract_id="adapter-mvp-contract",
    version="1.0.0",
    purpose="MVP adapter proof",
    allowed_goal_types=["repo_summary", "read_only_query"],
    required_context_fields=["run_id", "goal_type"],
    forbidden_context_fields=["secrets", "credentials"],
    allowed_output_schema={"type": "object"},
    forbidden_claims=["PASS", "executed", "approved"],
    allowed_action_proposals=["read_repo_info", "list_repo_files"],
    allowed_tool_proposals=["read_repo_info"],
)


class TestPromptContract:
    def test_known_contract_resolves(self):
        registry = PromptContractRegistry()
        registry.register(SAMPLE_CONTRACT)
        result = registry.resolve("adapter-mvp-contract")
        assert result is not None
        assert result.contract_id == "adapter-mvp-contract"

    def test_unknown_contract_blocked(self):
        registry = PromptContractRegistry()
        result = registry.resolve("nonexistent")
        assert result is None

    def test_wrong_version_blocked(self):
        registry = PromptContractRegistry()
        registry.register(SAMPLE_CONTRACT)
        result = registry.resolve("adapter-mvp-contract", version="2.0.0")
        assert result is None

    def test_matches_goal_type(self):
        assert SAMPLE_CONTRACT.matches_goal_type("repo_summary") is True
        assert SAMPLE_CONTRACT.matches_goal_type("write_file") is False

    def test_contract_has_required_fields(self):
        assert SAMPLE_CONTRACT.contract_id
        assert SAMPLE_CONTRACT.version
        assert SAMPLE_CONTRACT.purpose

    def test_contract_has_forbidden_claims(self):
        assert "PASS" in SAMPLE_CONTRACT.forbidden_claims

    def test_contract_to_dict(self):
        d = SAMPLE_CONTRACT.to_dict()
        assert d["contract_id"] == "adapter-mvp-contract"
        assert d["version"] == "1.0.0"

    def test_register_multiple_contracts(self):
        registry = PromptContractRegistry()
        c1 = PromptContract(contract_id="c1", purpose="test1")
        c2 = PromptContract(contract_id="c2", purpose="test2")
        registry.register(c1)
        registry.register(c2)
        assert len(registry.list_contracts()) == 2
