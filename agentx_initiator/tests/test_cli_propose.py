import pytest
from agentx_initiator.core.patch_proposal_generator import generate_proposal, generate_patch_proposal


def test_propose_logic_allowed():
    p = generate_proposal("add tests for governance")
    assert p.allowed
    assert p.non_mutating


def test_propose_logic_blocked():
    p = generate_proposal("autonomous self-modify L0")
    assert not p.allowed


def test_generate_patch_proposal_basic():
    spec = generate_patch_proposal(task="add tests for governance")
    assert spec.task == "add tests for governance"
