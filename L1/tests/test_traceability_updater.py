from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.traceability_updater import (
    TraceLink,
    TraceabilityGraph,
    TraceabilityUpdater,
    TraceabilityUpdaterError,
    build_traceability_graph,
)


def test_adds_link() -> None:
    updater = TraceabilityUpdater()
    updater.add_link("a", "b", "implements")
    graph = updater.get_graph()
    assert len(graph.links) == 1
    assert graph.links[0].source_id == "a"
    assert graph.links[0].target_id == "b"
    assert graph.links[0].relationship == "implements"


def test_get_graph_contains_nodes() -> None:
    updater = TraceabilityUpdater()
    updater.add_link("src", "tgt", "traces_to")
    graph = updater.get_graph()
    assert "src" in graph.nodes
    assert "tgt" in graph.nodes


def test_duplicate_link_ignored() -> None:
    updater = TraceabilityUpdater()
    updater.add_link("a", "b", "r")
    updater.add_link("a", "b", "r")
    assert len(updater.get_graph().links) == 1


def test_empty_graph() -> None:
    updater = TraceabilityUpdater()
    graph = updater.get_graph()
    assert graph.links == ()
    assert graph.nodes == ()


def test_multiple_links() -> None:
    updater = TraceabilityUpdater()
    updater.add_link("a", "b", "r1")
    updater.add_link("c", "d", "r2")
    assert len(updater.get_graph().links) == 2


def test_build_from_records_and_packets() -> None:
    from L1.controller.completion_record_writer import CompletionRecord
    from L1.controller.handoff_packet_builder import HandoffPacket

    cr = CompletionRecord(unit_id="U001", summary="s", evidence_total=2, evidence_passed=2, all_evidence_passed=True, status="completed")
    hp = HandoffPacket(packet_id="HOP-L1-001", fic_id="FIC-L1-PLAN-001", unit_id="U001", target_file="t.py", description="d", complexity="small", dependencies=())

    graph = build_traceability_graph((cr,), (hp,))
    assert len(graph.links) >= 1


def test_link_is_frozen() -> None:
    link = TraceLink(source_id="a", target_id="b", relationship="r")
    with pytest.raises(dataclasses.FrozenInstanceError):
        link.source_id = "changed"  # type: ignore[misc]


def test_graph_is_frozen() -> None:
    g = TraceabilityGraph(links=(), nodes=())
    with pytest.raises(dataclasses.FrozenInstanceError):
        g.nodes = ("x",)  # type: ignore[misc]


def test_traceability_updater_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/traceability_updater.py").read_text(encoding="utf-8")
    forbidden = [
        "import os",
        "from os",
        "import subprocess",
        "from subprocess",
        "import requests",
        "import urllib",
        "import socket",
        "import http",
    ]
    for imp in forbidden:
        assert imp not in source, f"forbidden import found: {imp}"


def test_nodes_are_sorted_unique() -> None:
    updater = TraceabilityUpdater()
    updater.add_link("z", "a", "r")
    updater.add_link("a", "b", "r")
    graph = updater.get_graph()
    assert graph.nodes == ("a", "b", "z")
