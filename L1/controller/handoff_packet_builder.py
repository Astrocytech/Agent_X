from __future__ import annotations

import dataclasses
import typing as _typing

from L1.controller.fic_generator import FicTemplate
from L1.controller.unit_planner import UnitPlan

__all__ = [
    "HandoffPacket",
    "HandoffPacketBuilder",
    "HandoffPacketBuilderError",
    "build_handoff_packets",
]


@dataclasses.dataclass(frozen=True)
class HandoffPacket:
    packet_id: str
    fic_id: str
    unit_id: str
    target_file: str
    description: str
    complexity: str
    dependencies: tuple[str, ...]
    status: str = "draft"


class HandoffPacketBuilderError(Exception):
    pass


class HandoffPacketBuilder:
    def build(
        self,
        templates: object,
        unit_plan: object,
    ) -> tuple[HandoffPacket, ...]:
        if not isinstance(templates, tuple):
            raise HandoffPacketBuilderError("templates must be a tuple")
        if not isinstance(unit_plan, UnitPlan):
            raise HandoffPacketBuilderError("unit_plan must be a UnitPlan")

        count = min(len(templates), len(unit_plan.units))
        packets: list[HandoffPacket] = []

        for i in range(count):
            t = templates[i]
            u = unit_plan.units[i]
            packets.append(
                HandoffPacket(
                    packet_id=f"HOP-L1-{i + 1:03d}",
                    fic_id=t.fic_id if isinstance(t, FicTemplate) else "",
                    unit_id=t.unit_id if isinstance(t, FicTemplate) else u.unit_id,
                    target_file=t.target_file if isinstance(t, FicTemplate) else "",
                    description=t.description if isinstance(t, FicTemplate) else u.description,
                    complexity=u.complexity.value,
                    dependencies=u.dependencies,
                )
            )

        return tuple(packets)


def build_handoff_packets(
    templates: tuple[FicTemplate, ...],
    unit_plan: UnitPlan,
) -> tuple[HandoffPacket, ...]:
    return HandoffPacketBuilder().build(templates, unit_plan)
