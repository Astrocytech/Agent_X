from agentx_evolve.model_runtime.runtime_policy import PromptCompatibility, PC_COMPATIBLE, PC_INCOMPATIBLE


def test_prompt_compatibility_defaults():
    pc = PromptCompatibility()
    assert pc.status == PC_COMPATIBLE
    assert pc.reason == ""


def test_prompt_compatibility_incompatible():
    pc = PromptCompatibility(status=PC_INCOMPATIBLE, reason="prompt too long")
    assert pc.status == PC_INCOMPATIBLE
    assert pc.reason == "prompt too long"


def test_prompt_compatibility_is_compatible():
    pc = PromptCompatibility()
    assert pc.is_compatible() is True
    pc2 = PromptCompatibility(status=PC_INCOMPATIBLE)
    assert pc2.is_compatible() is False


def test_pc_constants():
    assert PC_COMPATIBLE == "COMPATIBLE"
    assert PC_INCOMPATIBLE == "INCOMPATIBLE"
