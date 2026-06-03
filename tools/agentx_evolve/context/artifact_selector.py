from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from agentx_evolve.model.model_models import to_dict


@dataclass
class ArtifactMatch:
    artifact_id: str = ""
    artifact_type: str = ""
    description: str = ""
    relevance_score: float = 0.0
    reason: str = ""

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ArtifactSelectionResult:
    selected: list[ArtifactMatch] = field(default_factory=list)
    token_estimate: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class ArtifactSelector:
    def select(self, task_type: str, objective: str,
               available: list[dict]) -> ArtifactSelectionResult:
        result = ArtifactSelectionResult()
        obj_lower = objective.lower()
        for item in available:
            artifact_type = item.get("artifact_type", "")
            description = item.get("description", "")
            aid = item.get("artifact_id", "")
            score, reason = self._score(artifact_type, description, obj_lower)
            if score > 0:
                result.selected.append(ArtifactMatch(
                    artifact_id=aid, artifact_type=artifact_type,
                    description=description, relevance_score=score, reason=reason,
                ))
        return result

    def _score(self, artifact_type: str, description: str,
               objective_lower: str) -> tuple[float, str]:
        combined = (artifact_type + " " + description).lower()
        keywords = set(objective_lower.split())
        match_count = sum(1 for kw in keywords if kw in combined)
        if match_count > 0:
            return min(1.0, 0.4 + match_count * 0.1), f"Matches {match_count} keyword(s)"
        return 0.0, "No relevance"
