import pytest
from pathlib import Path
from agentx_initiator.core.governance_rules import apply_governance_rules, RULE_IDS
from agentx_initiator.core.governance_model import GovernanceRequest, GovernanceContext


def test_rule_ids_defined():
    assert len(RULE_IDS) > 0
    assert "GOV-001" in RULE_IDS
    assert "GOV-002" in RULE_IDS


def test_apply_governance_rules_allow(tmp_path):
    req = GovernanceRequest(action_type="GENERATE_REPORT", target_path=str(tmp_path / ".agentx-init/report.md"))
    ctx = GovernanceContext(repo_root=tmp_path, runtime_root=tmp_path / ".agentx-init")
    decision = apply_governance_rules(req, ctx)
    assert decision.decision == "ALLOW"


def test_apply_governance_rules_block_unknown(tmp_path):
    req = GovernanceRequest(action_type="UNKNOWN", target_path="")
    ctx = GovernanceContext(repo_root=tmp_path, runtime_root=tmp_path / ".agentx-init")
    decision = apply_governance_rules(req, ctx)
    assert decision.decision == "BLOCK"


def test_apply_governance_rules_block_outside_runtime(tmp_path):
    req = GovernanceRequest(action_type="WRITE_FILE", target_path=str(tmp_path / "outside.txt"))
    ctx = GovernanceContext(repo_root=tmp_path, runtime_root=tmp_path / ".agentx-init")
    decision = apply_governance_rules(req, ctx)
    assert decision.decision == "BLOCK"
    assert any(v.get("violation_type") == "OUTSIDE_RUNTIME_BOUNDARY" for v in decision.violations)


def test_apply_governance_rules_block_readonly_component(tmp_path):
    runtime = tmp_path / ".agentx-init"
    runtime.mkdir(parents=True, exist_ok=True)
    req = GovernanceRequest(action_type="WRITE_FILE", target_path=str(runtime / "test.txt"), source_component="RepositoryScanner")
    ctx = GovernanceContext(repo_root=tmp_path, runtime_root=runtime)
    decision = apply_governance_rules(req, ctx)
    assert decision.decision == "BLOCK"
    assert any(v.get("violation_type") == "READONLY_MUTATION" for v in decision.violations)
