import json
from agentx_initiator.core.knowledge_graph import build_graph
from agentx_initiator.core.paths import snapshot_file, ensure_state_dirs
from agentx_initiator.core.audit_log import append_event


def register(sub):
    p = sub.add_parser("graph", help="Build architecture knowledge graph")
    p.set_defaults(func=run)


def run(args):
    ensure_state_dirs()
    graph = build_graph()

    snap = snapshot_file("graph_snapshot_latest.json")
    snap.write_text(json.dumps(graph, indent=2))

    print(f"Graph written to {snap}")
    print(f"Nodes: {len(graph['nodes'])}")
    print(f"Edges: {len(graph['edges'])}")

    append_event({
        "event_type": "graph",
        "detail": f"Built knowledge graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges",
    })
