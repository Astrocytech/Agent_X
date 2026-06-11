"""Component ownership manifests and dependency direction enforcement.

Item 42 (35.1/35.2): Manifests declare component boundaries,
ownership, dependencies, and enforce dependency direction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ComponentManifest:
    name: str
    path: str
    description: str
    owner: str = "unassigned"
    layer: str = ""  # source | governance | evaluation | boundary | infrastructure
    depends_on: list[str] = field(default_factory=list)
    provides: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def allowed_to_depend_on(self, target: str) -> bool:
        """Layer dependency rules: infrastructure no deps, evaluation depends on governance, etc."""
        layers = {
            "source": 0,
            "governance": 1,
            "evaluation": 2,
            "boundary": 3,
            "infrastructure": 4,
        }
        source_layer = layers.get(self.layer, 99)
        target_layer = layers.get(target, -1)
        return source_layer > target_layer  # Higher layers can depend on lower ones


MANIFESTS: dict[str, ComponentManifest] = {}


def Register(manifest: ComponentManifest) -> None:
    MANIFESTS[manifest.name] = manifest


def Get(name: str) -> ComponentManifest | None:
    return MANIFESTS.get(name)


def CheckDirection(source: str, target: str) -> tuple[bool, str]:
    sm = MANIFESTS.get(source)
    tm = MANIFESTS.get(target)
    if not sm:
        return False, f"Unknown source component: {source}"
    if not tm:
        return False, f"Unknown target component: {target}"
    if sm.layer == tm.layer:
        return True, "Same layer, allowed"
    allowed = sm.allowed_to_depend_on(tm.layer)
    if not allowed:
        return False, (f"Dependency direction violation: {sm.layer} -> {tm.layer} "
                       f"(source '{source}' cannot depend on target '{target}')")
    return True, "Ok"


Register(ComponentManifest("source_docs", "docs/plans", "Source plans and documents",
                           owner="governance", layer="source"))
Register(ComponentManifest("benchmarks", "benchmarks", "Benchmark source and derived artifacts",
                           owner="governance", layer="source",
                           depends_on=["source_docs"]))
Register(ComponentManifest("schemas", "schemas", "Shared JSON schemas",
                           owner="governance", layer="source"))
Register(ComponentManifest("example_agents", "examples", "Example agent implementations",
                           owner="evolve", layer="source",
                           depends_on=["schemas"]))
Register(ComponentManifest("provenance", ".agentx-init", "Provenance and evidence records",
                           owner="governance", layer="governance",
                           depends_on=["source_docs", "schemas"]))
Register(ComponentManifest("event_logger", "tools/agentx_evolve/evidence",
                           "Append-only event logger",
                           owner="evolve", layer="governance",
                           depends_on=["schemas"]))
Register(ComponentManifest("guard_validators", "tools/agentx_evolve/validators",
                           "No-op, weak-test, secret, manual-insertion guards",
                           owner="evolve", layer="governance",
                           depends_on=["provenance", "event_logger"]))
Register(ComponentManifest("clean_workspace", "tools/agentx_evolve/clean_workspace",
                           "Clean workspace runner",
                           owner="evolve", layer="evaluation",
                           depends_on=["provenance"]))
Register(ComponentManifest("evaluation_harness", "tools/agentx_evolve/evaluation",
                           "Reusable evaluation harness",
                           owner="evolve", layer="evaluation",
                           depends_on=["fixture_manager"]))
Register(ComponentManifest("fixture_manager", "tools/agentx_evolve/evaluation",
                           "Canonical fixture management",
                           owner="evolve", layer="evaluation",
                           depends_on=["source_docs"]))
Register(ComponentManifest("tool_adapter", "tools/agentx_evolve/boundary",
                           "Unified tool-adapter boundary",
                           owner="evolve", layer="boundary"))
Register(ComponentManifest("scheduler", "tools/agentx_evolve/monitoring",
                           "Task queue and session scheduler",
                           owner="evolve", layer="infrastructure"))


def summary() -> list[dict]:
    return [{"name": m.name, "path": m.path, "layer": m.layer, "owner": m.owner,
             "depends_on": m.depends_on} for m in MANIFESTS.values()]
