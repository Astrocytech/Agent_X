from agentx_initiator.core.repo_scanner import scan_repo


def test_cli_scan_logic():
    scan = scan_repo()
    assert scan.total_files > 0
    assert len(scan.layers) == 3
