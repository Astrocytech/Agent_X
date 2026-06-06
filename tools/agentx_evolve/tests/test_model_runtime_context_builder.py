from agentx_evolve.model_runtime.context_window_compatibility import ContextBuilderCheck, CBC_PASS, CBC_FAIL


def test_context_builder_check_defaults():
    cbc = ContextBuilderCheck()
    assert cbc.status == CBC_PASS
    assert cbc.reason == ""


def test_context_builder_check_fail():
    cbc = ContextBuilderCheck(status=CBC_FAIL, reason="context window exceeded")
    assert cbc.status == CBC_FAIL
    assert cbc.reason == "context window exceeded"


def test_context_builder_check_passed():
    cbc = ContextBuilderCheck()
    assert cbc.passed() is True
    cbc2 = ContextBuilderCheck(status=CBC_FAIL)
    assert cbc2.passed() is False


def test_cbc_constants():
    assert CBC_PASS == "PASS"
    assert CBC_FAIL == "FAIL"
