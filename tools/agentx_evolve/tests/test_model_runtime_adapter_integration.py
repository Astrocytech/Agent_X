from agentx_evolve.model_runtime.runtime_mode import RuntimeMode, resolve_runtime_mode, RM_LOCAL, RM_HOSTED


def test_runtime_mode_defaults():
    rm = RuntimeMode()
    assert rm.mode == RM_LOCAL
    assert rm.hosted_fallback_allowed is False
    assert rm.network_allowed is False


def test_runtime_mode_hosted():
    rm = RuntimeMode(mode=RM_HOSTED, hosted_fallback_allowed=True, network_allowed=True)
    assert rm.mode == RM_HOSTED
    assert rm.hosted_fallback_allowed is True
    assert rm.network_allowed is True


def test_resolve_runtime_mode_default():
    result = resolve_runtime_mode({}, {})
    assert result["runtime_mode"] == "LOCAL_ONLY"
    assert result["hosted_fallback_allowed"] is False


def test_resolve_runtime_mode_disabled():
    result = resolve_runtime_mode({}, {"runtime_mode": "DISABLED"})
    assert result["runtime_mode"] == "DISABLED"


def test_rm_constants():
    assert RM_LOCAL == "LOCAL"
    assert RM_HOSTED == "HOSTED"
