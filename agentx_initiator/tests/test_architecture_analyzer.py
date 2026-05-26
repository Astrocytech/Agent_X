from agentx_initiator.core.architecture_analyzer import analyze_architecture


def test_analyze_architecture():
    report = analyze_architecture()
    assert report.layer_count >= 3
    assert report.valid_layer_structure is not None
    assert report.l0_independent
