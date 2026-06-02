import pytest
from agentx_initiator.core.patch_proposal_generator import generate_proposal


pytestmark = pytest.mark.skip(reason="PM2 patch_proposal_generator not active in Product Milestone 1")


def test_propose_logic_allowed():
    p = generate_proposal("add tests for governance")
    assert p.allowed
    assert p.non_mutating


def test_propose_logic_blocked():
    p = generate_proposal("autonomous self-modify L0")
    assert not p.allowed
