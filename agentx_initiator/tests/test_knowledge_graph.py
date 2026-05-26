from agentx_initiator.core.knowledge_graph import build_graph


def test_build_graph():
    graph = build_graph()
    assert "nodes" in graph
    assert "edges" in graph
    assert "metadata" in graph
    assert len(graph["nodes"]) > 0
