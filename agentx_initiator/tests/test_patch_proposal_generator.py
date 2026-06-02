import pytest
from agentx_initiator.core.patch_proposal_generator import generate_proposal, generate_patch_proposal
from agentx_initiator.core.patch_proposal_model import PatchSpec


def test_generate_proposal():
    proposal = generate_proposal("add unit tests for L1 governance")
    assert proposal.task == "add unit tests for L1 governance"
    assert proposal.non_mutating


def test_proposal_blocks_r4():
    proposal = generate_proposal("modify L0 core kernel")
    assert not proposal.allowed
    assert proposal.risk_level == "R4"


def test_generate_patch_proposal_returns_spec():
    spec = generate_patch_proposal(task="add tests for governance")
    assert isinstance(spec, PatchSpec)
    assert spec.task == "add tests for governance"


def test_generate_patch_proposal_has_actions():
    spec = generate_patch_proposal(task="read the scan output")
    assert len(spec.actions) > 0
