import json
import sys
import io
import argparse

from agentx_initiator.cli.commands.graph import register, run
from agentx_initiator.core.path_registry import get_path


def _make_args(mode="build", node_id="", node_type="", edge_type="",
               incoming="", outgoing="", json_output=False, output_format="text"):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    register(sub)
    args_list = ["graph", mode]
    if node_id:
        args_list.extend(["--node-id", node_id])
    if node_type:
        args_list.extend(["--node-type", node_type])
    if edge_type:
        args_list.extend(["--edge-type", edge_type])
    if incoming:
        args_list.extend(["--incoming", incoming])
    if outgoing:
        args_list.extend(["--outgoing", outgoing])
    if json_output:
        args_list.append("--json")
    if output_format != "text":
        args_list.extend(["--output-format", output_format])
    return parser.parse_args(args_list)


def _capture_run(args):
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        run(args)
    except SystemExit:
        pass
    sys.stdout = old_stdout
    return captured.getvalue()


def test_graph_registers_subparser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    register(sub)
    parsed = parser.parse_args(["graph", "build"])
    assert parsed.command == "graph"
    assert parsed.mode == "build"
    assert parsed.func == run


def test_graph_build_prints_summary():
    output = _capture_run(_make_args("build"))
    assert "Knowledge Graph" in output
    assert "Nodes:" in output
    assert "Edges:" in output
    assert "Integrity:" in output


def test_graph_build_json_output():
    output = _capture_run(_make_args("build", json_output=True))
    data = json.loads(output)
    assert "status" in data
    assert "node_count" in data
    assert "edge_count" in data
    assert data["node_count"] > 0


def test_graph_build_writes_artifact_files():
    _capture_run(_make_args("build"))
    snap = get_path("runtime_root") / "graph" / "graph_snapshot_latest.json"
    assert snap.exists()
    data = json.loads(snap.read_text())
    assert data.get("node_count", 0) > 0
    man = get_path("runtime_root") / "graph" / "graph_manifest_latest.json"
    assert man.exists()
    integrity = get_path("runtime_root") / "graph" / "graph_integrity_latest.json"
    assert integrity.exists()
    idx = get_path("runtime_root") / "graph" / "graph_index.json"
    assert idx.exists()


def test_graph_status_text_output():
    output = _capture_run(_make_args("status"))
    assert "Graph Status" in output
    assert "Nodes:" in output


def test_graph_status_json_output():
    output = _capture_run(_make_args("status", json_output=True))
    data = json.loads(output)
    assert "node_count" in data
    assert "edge_types" in data


def test_graph_query_returns_results():
    output = _capture_run(_make_args("query"))
    assert "Query results" in output


def test_graph_query_json_output():
    output = _capture_run(_make_args("query", json_output=True))
    data = json.loads(output)
    assert "result_count" in data


def test_graph_query_by_node_type():
    _capture_run(_make_args("build"))
    output = _capture_run(_make_args("query", node_type="COMPONENT"))
    assert "Query results" in output
    assert "COMPONENT" in output
