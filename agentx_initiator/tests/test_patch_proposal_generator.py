from agentx_initiator.core.patch_proposal_generator import generate_proposal


def test_generate_proposal():
    proposal = generate_proposal("add unit tests for L1 governance")
    assert proposal.task == "add unit tests for L1 governance"
    assert proposal.non_mutating


def test_proposal_blocks_r4():
    proposal = generate_proposal("modify L0 core kernel")
    assert not proposal.allowed
    assert proposal.risk_level == "R4"
