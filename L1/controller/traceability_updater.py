from __future__ import annotations

import dataclasses
import typing as _typing

__all__ = [
    "TraceLink",
    "TraceabilityGraph",
    "TraceabilityUpdater",
    "TraceabilityUpdaterError",
    "build_traceability_graph",
]


@dataclasses.dataclass(frozen=True)
class TraceLink:
    source_id: str
    target_id: str
    relationship: str


@dataclasses.dataclass(frozen=True)
class TraceabilityGraph:
    links: tuple[TraceLink, ...]
    nodes: tuple[str, ...]


class TraceabilityUpdaterError(Exception):
    pass


class TraceabilityUpdater:
    def __init__(self) -> None:
        self._links: list[TraceLink] = []
        self._seen: set[tuple[str, str, str]] = set()

    def add_link(self, source: str, target: str, relationship: str) -> None:
        key = (source, target, relationship)
        if key in self._seen:
            return
        self._seen.add(key)
        self._links.append(
            TraceLink(
                source_id=source,
                target_id=target,
                relationship=relationship,
            )
        )

    def get_graph(self) -> TraceabilityGraph:
        nodes: set[str] = set()
        for link in self._links:
            nodes.add(link.source_id)
            nodes.add(link.target_id)
        return TraceabilityGraph(
            links=tuple(self._links),
            nodes=tuple(sorted(nodes)),
        )


def build_traceability_graph(
    completion_records: tuple["CompletionRecord", ...],  # type: ignore[name-defined]  # noqa: F821
    handoff_packets: tuple["HandoffPacket", ...],  # type: ignore[name-defined]  # noqa: F821
) -> TraceabilityGraph:
    updater = TraceabilityUpdater()
    for packet in handoff_packets:
        for record in completion_records:
            if packet.unit_id == record.unit_id:
                updater.add_link(packet.packet_id, record.unit_id, "implements")
    for record in completion_records:
        updater.add_link(record.unit_id, f"evidence:{record.status}", "traces_to")
    return updater.get_graph()
