from agentx_initiator.core.repo_model import RepoScan, LayerEntry, ArchitectureReport


def test_repo_scan_creation():
    scan = RepoScan(root="/test", layers=[], total_files=10, source_files=5, doc_files=3, test_files=2)
    assert scan.total_files == 10
    assert scan.source_files == 5


def test_layer_entry_creation():
    entry = LayerEntry(layer="L0", path="/test/L0", purpose="seed", file_count=5, has_readme=True)
    assert entry.layer == "L0"
    assert entry.has_readme


def test_architecture_report():
    r = ArchitectureReport(layers=[], layer_count=0, valid_layer_structure=True, l0_independent=True, l1_separated=True, l2_contains_active_runtime=False)
    assert r.valid_layer_structure
    assert r.l0_independent
