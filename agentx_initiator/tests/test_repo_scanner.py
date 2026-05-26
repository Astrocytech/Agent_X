from agentx_initiator.core.repo_scanner import scan_repo


def test_scan_repo_returns_scan():
    scan = scan_repo()
    assert scan.root.endswith("Agent_X")
    assert len(scan.layers) > 0
    assert scan.total_files > 0


def test_scan_includes_layers():
    scan = scan_repo()
    layer_names = [l.layer for l in scan.layers]
    assert "L0" in layer_names
    assert "L1" in layer_names
    assert "L2" in layer_names
