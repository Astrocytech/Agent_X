import pytest
from pathlib import Path
from agentx_initiator.core.governance_engine import run_governance_checks, evaluate_governance
from agentx_initiator.core.governance_model import GovernanceRequest, GovernanceContext


def test_governance_checks_return_list():
    results = run_governance_checks()
    assert isinstance(results, list)
    assert len(results) > 0


def test_each_check_has_required_fields():
    results = run_governance_checks()
    for r in results:
        assert "check" in r
        assert "passed" in r
        assert "detail" in r


def test_evaluate_governance_no_context(tmp_path):
    req = GovernanceRequest(action_type="GENERATE_REPORT", target_path=str(tmp_path / ".agentx-init/report.md"))
    ctx = GovernanceContext(repo_root=tmp_path, runtime_root=tmp_path / ".agentx-init")
    decision = evaluate_governance(req, ctx)
    assert decision.status == "PASS"
    assert decision.decision == "ALLOW"


def test_evaluate_governance_block_unknown_action(tmp_path):
    req = GovernanceRequest(action_type="UNKNOWN", target_path="")
    ctx = GovernanceContext(repo_root=tmp_path, runtime_root=tmp_path / ".agentx-init")
    decision = evaluate_governance(req, ctx)
    assert decision.decision == "BLOCK"
