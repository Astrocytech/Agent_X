from agentx_initiator.core.repo_model import ArchitectureReport, LayerEntry
from agentx_initiator.core.repo_scanner import scan_repo
from agentx_initiator.core.layer_mapper import build_layer_map


def analyze_architecture() -> ArchitectureReport:
    scan = scan_repo()
    mapping = build_layer_map()

    layers = scan.layers
    l0_independent = True
    l1_separated = True
    l2_runtime = False
    risks = []

    for name, info in mapping.items():
        for v in info.get("violations", []):
            if name == "L2" and "runtime" in v.lower():
                l2_runtime = True
            risks.append({
                "layer": name,
                "concern": v,
                "severity": "medium",
            })

    if not risks:
        for entry in layers:
            if entry.layer == "unknown" and entry.file_count > 0:
                risks.append({
                    "layer": "unknown",
                    "concern": f"{entry.file_count} file(s) unclassified",
                    "severity": "low",
                })

    return ArchitectureReport(
        layers=layers,
        layer_count=len(layers),
        valid_layer_structure=all(l.has_readme for l in layers),
        l0_independent=l0_independent,
        l1_separated=l1_separated,
        l2_contains_active_runtime=l2_runtime,
        risks=risks,
    )
