from agentx_evolve.model_runtime.runtime_policy import RuntimePolicy, RP_ALLOW, RP_BLOCK


def test_runtime_policy_defaults():
    rp = RuntimePolicy()
    assert rp.mode == RP_ALLOW
    assert rp.policy_id == ""


def test_runtime_policy_block():
    rp = RuntimePolicy(policy_id="pol-1", mode=RP_BLOCK)
    assert rp.policy_id == "pol-1"
    assert rp.mode == RP_BLOCK


def test_runtime_policy_evaluate():
    rp = RuntimePolicy(mode=RP_BLOCK)
    result = rp.evaluate({})
    assert result == RP_BLOCK


def test_rp_constants():
    assert RP_ALLOW == "ALLOW"
    assert RP_BLOCK == "BLOCK"
