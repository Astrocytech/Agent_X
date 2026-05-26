from agentx_initiator.core.repo_scanner import scan_repo
from agentx_initiator.core.architecture_analyzer import analyze_architecture


def test_status_logic():
    scan = scan_repo()
    arch = analyze_architecture()
    assert scan.total_files > 0
    assert arch.layer_count >= 0
