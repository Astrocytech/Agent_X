from agentx_initiator.core.layer_mapper import build_layer_map, LAYER_RULES


def test_build_layer_map():
    mapping = build_layer_map()
    assert "L0" in mapping
    assert "L1" in mapping
    assert "L2" in mapping


def test_layer_rules_defined():
    assert "L0" in LAYER_RULES
    assert LAYER_RULES["L0"]["is_protected"]
    assert "L2" in LAYER_RULES
    assert "forbidden_runtime_dirs" in LAYER_RULES["L2"]
