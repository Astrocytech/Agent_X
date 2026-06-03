from agentx_evolve.model_runtime.runtime_policy import ToolCompatibility, TC_SUPPORTED, TC_UNSUPPORTED


def test_tool_compatibility_defaults():
    tc = ToolCompatibility()
    assert tc.status == TC_SUPPORTED
    assert tc.reason == ""


def test_tool_compatibility_unsupported():
    tc = ToolCompatibility(status=TC_UNSUPPORTED, reason="tool not in allowlist")
    assert tc.status == TC_UNSUPPORTED
    assert tc.reason == "tool not in allowlist"


def test_tool_compatibility_is_supported():
    tc = ToolCompatibility()
    assert tc.is_supported() is True
    tc2 = ToolCompatibility(status=TC_UNSUPPORTED)
    assert tc2.is_supported() is False


def test_tc_constants():
    assert TC_SUPPORTED == "SUPPORTED"
    assert TC_UNSUPPORTED == "UNSUPPORTED"
