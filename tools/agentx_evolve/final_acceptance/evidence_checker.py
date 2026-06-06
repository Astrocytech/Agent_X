from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.final_acceptance.acceptance_models import STATUS_PASS, STATUS_FAIL

__all__ = [
    "EvidenceChecker",
]


@dataclass
class EvidenceChecker:
    evidence_map: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def add_evidence(self, layer: str, evidence: dict[str, Any]) -> None:
        if layer not in self.evidence_map:
            self.evidence_map[layer] = []
        self.evidence_map[layer].append(evidence)

    def check_layer(self, layer: str) -> dict[str, Any]:
        items = self.evidence_map.get(layer, [])
        if not items:
            return {
                "layer": layer,
                "status": STATUS_FAIL,
                "found": 0,
                "required": 0,
                "message": "no evidence found for layer",
            }
        ...
        return {
            "layer": layer,
            "status": STATUS_PASS,
            "found": len(items),
            "required": 0,
            "message": "evidence check passed",
        }
