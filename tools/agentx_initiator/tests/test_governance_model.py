import pytest
from pathlib import Path
from agentx_initiator.core.governance_model import GovernanceRequest, GovernanceContext, GovernanceEvidence, GovernanceViolation, GovernanceDecision


def test_governance_request_defaults():
    req = GovernanceRequest()
    assert req.action_type == "UNKNOWN"
    assert req.target_path is None


def test_governance_context_defaults():
    ctx = GovernanceContext()
    assert ctx.repo_root == Path(".")
    assert ctx.runtime_root == Path(".agentx-init")


def test_governance_evidence_to_dict():
    ev = GovernanceEvidence(evidence_id="ev-001", claim="test claim", supports_decision="BLOCK")
    d = ev.to_dict()
    assert d["evidence_id"] == "ev-001"
    assert d["claim"] == "test claim"


def test_governance_violation_to_dict():
    v = GovernanceViolation(violation_id="v-001", violation_type="L0_MODIFICATION", message="L0 change")
    d = v.to_dict()
    assert d["violation_type"] == "L0_MODIFICATION"


def test_governance_decision_defaults():
    d = GovernanceDecision()
    assert d.decision == "BLOCK"
    assert d.violations == []
