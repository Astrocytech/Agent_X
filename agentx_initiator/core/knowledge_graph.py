import json
from datetime import datetime
from agentx_initiator.core.repo_scanner import scan_repo
from agentx_initiator.core.layer_mapper import build_layer_map


def build_graph() -> dict:
    scan = scan_repo()
    mapping = build_layer_map()

    nodes = []
    edges = []

    for layer in scan.layers:
        node_id = f"layer:{layer.layer}"
        nodes.append({
            "id": node_id,
            "type": "layer",
            "label": layer.layer,
            "purpose": layer.purpose,
            "file_count": layer.file_count,
        })

        dirs = mapping.get(layer.layer, {}).get("directories", [])
        for d in dirs:
            dir_id = f"dir:{layer.layer}/{d}"
            nodes.append({
                "id": dir_id,
                "type": "directory",
                "label": d,
            })
            edges.append({
                "source": node_id,
                "target": dir_id,
                "relation": "contains",
            })

    for i in range(len(scan.layers) - 1):
        edges.append({
            "source": f"layer:{scan.layers[i].layer}",
            "target": f"layer:{scan.layers[i + 1].layer}",
            "relation": "governs",
        })

    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "type": "architecture_graph",
        },
        "nodes": nodes,
        "edges": edges,
    }
